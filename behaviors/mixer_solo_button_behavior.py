import midi
import mixer

from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal import mcu_buttons
from utilities.track_banking_manager import TrackBankingManager
from device_hal.mcu_device import McuDevice


class MixerSoloButtonBehavior(McuBaseBehavior):
    """Behavior for handling SOLO button presses and updating SOLO button LEDs based on track solo status."""

    def __init__(self, mcuDevice: McuDevice, trackBankingManager: TrackBankingManager):
        super().__init__(mcuDevice)
        self.__trackBanking = trackBankingManager

    def OnEnable(self):
        super().OnEnable()
        self.__trackBanking.AddTrackChangeSubscriber(self._onTrackBankChange)

    def OnDisable(self):
        self.__trackBanking.RemoveTrackChangeSubscriber(self._onTrackBankChange)
        super().OnDisable()

    def _onTrackBankChange(self, newFirstTrack):
        """Called when track banking changes, update SOLO buttons."""
        self._updateSoloButtons()

    def OnRefresh(self, flags):
        super().OnRefresh(flags)
        
        # Update SOLO button LEDs when mixer controls change
        if flags & midi.HW_Dirty_Mixer_Controls:
            self._updateSoloButtons()

    def OnMidiMsg(self, event):
        """Handle SOLO button presses to solo/unsolo tracks in FL Studio mixer."""
        if event.midiId == midi.MIDI_NOTEON and event.data2 > 0:
            # Check if this is a SOLO button press
            if event.data1 in [mcu_buttons.Solo_1, mcu_buttons.Solo_2, mcu_buttons.Solo_3, mcu_buttons.Solo_4,
                               mcu_buttons.Solo_5, mcu_buttons.Solo_6, mcu_buttons.Solo_7, mcu_buttons.Solo_8]:
                # Calculate which track index was pressed
                solo_button_index = event.data1 - mcu_buttons.Solo_1
                virtualTrackIndex = self.__trackBanking.GetTrackIndex(solo_button_index)
                
                assert virtualTrackIndex != -1, "Invalid track index for SOLO button press"
                # Only solo if the track exists in FL Studio
                if self.__trackBanking.VirtualTrackExists(virtualTrackIndex):
                    mixer.soloTrack(midi.TrackNum_Master + virtualTrackIndex, midi.fxSoloToggle, midi.fxSoloModeWithSourceTracks)
                # TODO: allow multiple solo tracks with shift; solo should be based on SHIFT value: midi.fxSoloModeWithSourceTracks if self.Shift else midi.fxSoloModeWithDestTracks
                
                event.handled = True
                return event

        return super().OnMidiMsg(event)

    def _updateSoloButtons(self):
        """Update all SOLO button LEDs to reflect current track solo status."""
        virtualTrackIndexes = self.__trackBanking.GetTrackIndexes()
        
        for virtualIndex in virtualTrackIndexes:
            track = self.__trackBanking.GetHardwareTrack(virtualIndex)
            if track is not None and track.buttons is not None:
                # Determine if this track is soloed
                isSolo = False
                if (self.__trackBanking.VirtualTrackExists(virtualIndex)):
                    isSolo = mixer.isTrackSolo(midi.TrackNum_Master + virtualIndex)
                track.buttons.SetSoloButton(isSolo)
