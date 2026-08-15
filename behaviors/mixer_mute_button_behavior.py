import midi
import mixer

from behaviors.mixer_banked_track_base_bahavior import MixerBankedTrackBaseBehavior
from device_hal import mcu_buttons
from utilities.track_banking_manager import TrackBankingManager
from device_hal.mcu_device import McuDevice


class MixerMuteButtonBehavior(MixerBankedTrackBaseBehavior):
    """Behavior for handling MUTE button presses and updating MUTE button LEDs based on track mute status."""

    def __init__(self, mcuDevice: McuDevice, trackBankingManager: TrackBankingManager):
        super().__init__(mcuDevice, trackBankingManager)

    def OnEnable(self):
        super().OnEnable()

    def OnDisable(self):
        for track in self.McuDevice.tracks:
            if track is not None and track.buttons is not None:
                track.buttons.SetMuteButton(False)
        super().OnDisable()

    def Update(self):
        """Called by base class when track banking changes or when tracks are marked dirty, updates MUTE buttons."""
        self._updateMuteButtons()

    def OnMidiMsg(self, event):
        """Handle MUTE button presses to mute/unmute tracks in FL Studio mixer."""
        if event.midiId == midi.MIDI_NOTEON and event.data2 > 0:
            # Check if this is a MUTE button press
            if event.data1 in [mcu_buttons.Mute_1, mcu_buttons.Mute_2, mcu_buttons.Mute_3, mcu_buttons.Mute_4,
                               mcu_buttons.Mute_5, mcu_buttons.Mute_6, mcu_buttons.Mute_7, mcu_buttons.Mute_8]:
                # Calculate which track index was pressed
                mute_button_index = event.data1 - mcu_buttons.Mute_1
                virtualTrackIndex = self.TrackBanking.GetTrackIndex(mute_button_index)
                
                assert virtualTrackIndex != -1, "Invalid track index for MUTE button press"
                # Only mute if the track exists in FL Studio
                if self.TrackBanking.VirtualTrackExists(virtualTrackIndex) and event.pmeFlags & midi.PME_System_Safe:
                    mixer.muteTrack(midi.TrackNum_Master + virtualTrackIndex)
                
                event.handled = True
                return event

        return super().OnMidiMsg(event)

    def _updateMuteButtons(self):
        """Update all MUTE button LEDs to reflect current track mute status."""
        virtualTrackIndexes = self.TrackBanking.GetTrackIndexes()
        
        for virtualIndex in virtualTrackIndexes:
            track = self.TrackBanking.GetHardwareTrack(virtualIndex)
            if track is not None and track.buttons is not None:
                # Determine if this track is muted (muted when NOT enabled)
                isMuted = False
                if (self.TrackBanking.VirtualTrackExists(virtualIndex)):
                    isMuted = mixer.isTrackMuted(midi.TrackNum_Master + virtualIndex)
                track.buttons.SetMuteButton(isMuted)
