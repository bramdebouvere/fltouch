from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal.mcu_device import McuDevice
from utilities.track_banking_manager import TrackBankingManager

class MenuSelectLedBehavior(McuBaseBehavior):
    """Lights each channel's SELECT LED for every banked menu item, as a visual cue that it can be picked."""

    def __init__(self, mcuDevice: McuDevice, menuBankingManager: TrackBankingManager):
        super().__init__(mcuDevice)
        self._menuBanking = menuBankingManager

    def OnEnable(self):
        super().OnEnable()
        self._menuBanking.AddTrackChangeSubscriber(self._onTrackBankChange)
        self.Update()

    def OnDisable(self):
        self._menuBanking.RemoveTrackChangeSubscriber(self._onTrackBankChange)

        for hardwareIndex in range(self._menuBanking.GetHardwareTrackCount()):
            track = self.McuDevice.GetTrack(hardwareIndex)
            if track is not None and track.buttons is not None:
                track.buttons.SetSelectButton(False)
        
        super().OnDisable()

    def _onTrackBankChange(self, newFirstTrack):
        self.Update()

    def Update(self):
        """Light the SELECT LED for every banked position with a menu item."""
        for virtualIndex in self._menuBanking.GetTrackIndexes():
            track = self._menuBanking.GetHardwareTrack(virtualIndex)
            if track is not None and track.buttons is not None:
                track.buttons.SetSelectButton(self._menuBanking.VirtualTrackExists(virtualIndex))
