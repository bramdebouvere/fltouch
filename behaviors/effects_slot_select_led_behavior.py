import midi
import mixer

from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal.mcu_device import McuDevice
from utilities.track_banking_manager import TrackBankingManager

class EffectsSlotSelectLedBehavior(McuBaseBehavior):
    """Lights each channel's SELECT LED for slots that hold a valid plugin, as a visual cue that it can be opened."""

    def __init__(self, mcuDevice: McuDevice, slotBankingManager: TrackBankingManager):
        super().__init__(mcuDevice)
        self._slotBanking = slotBankingManager

    def OnEnable(self):
        super().OnEnable()
        self._slotBanking.AddTrackChangeSubscriber(self._onTrackBankChange)
        self.Update()

    def OnDisable(self):
        self._slotBanking.RemoveTrackChangeSubscriber(self._onTrackBankChange)

        for hardwareIndex in range(self._slotBanking.GetHardwareTrackCount()):
            track = self.McuDevice.GetTrack(hardwareIndex)
            if track is not None and track.buttons is not None:
                track.buttons.SetSelectButton(False)
                
        super().OnDisable()

    def _onTrackBankChange(self, newFirstTrack):
        self.Update()

    def OnRefresh(self, flags):
        super().OnRefresh(flags)

        # A selection change retargets to another track's slots, and plugins can be added/removed/swapped
        if flags & (midi.HW_Dirty_Mixer_Sel | midi.HW_Dirty_Mixer_Controls | midi.HW_Dirty_Names):
            self.Update()

    def Update(self):
        """Light the SELECT LED for every banked slot that holds a valid plugin."""
        track = mixer.trackNumber()
        for virtualIndex in self._slotBanking.GetTrackIndexes():
            hardwareTrack = self._slotBanking.GetHardwareTrack(virtualIndex)
            if hardwareTrack is None or hardwareTrack.buttons is None:
                continue

            hasPlugin = self._slotBanking.VirtualTrackExists(virtualIndex) and mixer.isTrackPluginValid(track, virtualIndex)
            hardwareTrack.buttons.SetSelectButton(hasPlugin)
