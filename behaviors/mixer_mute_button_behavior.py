import midi
import mixer

from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal import mcu_buttons
from utilities.track_banking_manager import TrackBankingManager
from device_hal.mcu_device import McuDevice


class MixerMuteButtonBehavior(McuBaseBehavior):
    """Behavior for handling MUTE button presses and updating MUTE button LEDs based on track mute status."""

    def __init__(self, mcuDevice: McuDevice, trackBankingManager: TrackBankingManager):
        super().__init__(mcuDevice)
        self.__trackBanking = trackBankingManager

    def OnEnable(self):
        super().OnEnable()
        self.__trackBanking.AddTrackChangeSubscriber(self._onTrackBankChange)

    def OnDisable(self):
        self.__trackBanking.RemoveTrackChangeSubscriber(self._onTrackBankChange)
        # TODO: later we'll need to determine if we need to turn the button light off again when we disable the behavior.
        super().OnDisable()

    def _onTrackBankChange(self, newFirstTrack):
        """Called when track banking changes, update MUTE buttons."""
        self._updateMuteButtons()

    def OnRefresh(self, flags):
        super().OnRefresh(flags)
        
        # Update MUTE button LEDs when mixer controls change
        if flags & midi.HW_Dirty_Mixer_Controls:
            self._updateMuteButtons()

    def OnMidiMsg(self, event):
        """Handle MUTE button presses to mute/unmute tracks in FL Studio mixer."""
        if event.midiId == midi.MIDI_NOTEON and event.data2 > 0:
            # Check if this is a MUTE button press
            if event.data1 in [mcu_buttons.Mute_1, mcu_buttons.Mute_2, mcu_buttons.Mute_3, mcu_buttons.Mute_4,
                               mcu_buttons.Mute_5, mcu_buttons.Mute_6, mcu_buttons.Mute_7, mcu_buttons.Mute_8]:
                # Calculate which track index was pressed
                mute_button_index = event.data1 - mcu_buttons.Mute_1
                virtualTrackIndex = self.__trackBanking.GetTrackIndex(mute_button_index)
                
                assert virtualTrackIndex != -1, "Invalid track index for MUTE button press"
                # Only mute if the track exists in FL Studio
                if self.__trackBanking.VirtualTrackExists(virtualTrackIndex):
                    mixer.muteTrack(midi.TrackNum_Master + virtualTrackIndex)
                
                event.handled = True
                return event

        return super().OnMidiMsg(event)

    def _updateMuteButtons(self):
        """Update all MUTE button LEDs to reflect current track mute status."""
        virtualTrackIndexes = self.__trackBanking.GetTrackIndexes()
        
        for virtualIndex in virtualTrackIndexes:
            track = self.__trackBanking.GetHardwareTrack(virtualIndex)
            if track is not None and track.buttons is not None:
                # Determine if this track is muted (muted when NOT enabled)
                isMuted = False
                if (self.__trackBanking.VirtualTrackExists(virtualIndex)):
                    isMuted = mixer.isTrackMuted(midi.TrackNum_Master + virtualIndex)
                track.buttons.SetMuteButton(isMuted)