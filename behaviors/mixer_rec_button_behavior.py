import midi
import mixer
import transport
from behaviors.mcu_mixer_screen_behavior import McuMixerScreenBehavior
from behaviors.mixer_banked_track_base_bahavior import MixerBankedTrackBaseBehavior
from device_hal import mcu_buttons
from utilities import transliteration
from utilities.track_banking_manager import TrackBankingManager
from device_hal.mcu_device import McuDevice


class MixerRecButtonBehavior(MixerBankedTrackBaseBehavior):
    """Behavior for handling REC button presses and updating REC button LEDs based on track arm status."""

    def __init__(self, mcuDevice: McuDevice, trackBankingManager: TrackBankingManager, screenBehavior: McuMixerScreenBehavior):
        super().__init__(mcuDevice, trackBankingManager)
        self.__screenBehavior = screenBehavior

    def Update(self):
        """Called by base class when track banking changes or when tracks are marked dirty, updates REC buttons."""
        self._updateRecButtons()

    def OnDisable(self):
        for track in self.McuDevice.tracks:
            if track is not None and track.buttons is not None:
                track.buttons.SetArmButton(False, False)
        super().OnDisable()

    def OnMidiMsg(self, event):
        """Handle REC button presses to arm/unarm tracks for recording in FL Studio mixer."""
        if event.midiId == midi.MIDI_NOTEON and event.data2 > 0:
            # Check if this is a REC button press
            if event.data1 in [mcu_buttons.Record_1, mcu_buttons.Record_2, mcu_buttons.Record_3, mcu_buttons.Record_4,
                               mcu_buttons.Record_5, mcu_buttons.Record_6, mcu_buttons.Record_7, mcu_buttons.Record_8]:
                # Calculate which track index was pressed
                rec_button_index = event.data1 - mcu_buttons.Record_1
                virtualTrackIndex = self.TrackBanking.GetTrackIndex(rec_button_index)
                
                assert virtualTrackIndex != -1, "Invalid track index for REC button press"
                # Only arm if the track exists in FL Studio
                if self.TrackBanking.VirtualTrackExists(virtualTrackIndex) and event.pmeFlags & midi.PME_System_Safe:
                    mixer.armTrack(midi.TrackNum_Master + virtualTrackIndex)
                    if mixer.isTrackArmed(midi.TrackNum_Master + virtualTrackIndex):
                        self.__screenBehavior.OnSendTempMsg(transliteration.GetAsciiSafeTrackName(midi.TrackNum_Master + virtualTrackIndex) + ' recording')
                    else:
                        self.__screenBehavior.OnSendTempMsg(transliteration.GetAsciiSafeTrackName(midi.TrackNum_Master + virtualTrackIndex) + ' unarmed')
                
                event.handled = True
                return event

        return super().OnMidiMsg(event)

    def _updateRecButtons(self):
        """Update all REC button LEDs to reflect current track arm status."""
        
        isRecording = transport.isRecording()
        virtualTrackIndexes = self.TrackBanking.GetTrackIndexes()
        
        for virtualIndex in virtualTrackIndexes:
            track = self.TrackBanking.GetHardwareTrack(virtualIndex)
            if track is not None and track.buttons is not None:
                # Determine if this track is armed
                isArmed = False
                if (self.TrackBanking.VirtualTrackExists(virtualIndex)):
                    isArmed = mixer.isTrackArmed(midi.TrackNum_Master + virtualIndex)
                track.buttons.SetArmButton(isArmed, isRecording)
