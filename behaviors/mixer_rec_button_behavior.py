import midi
import mixer
import transport

from behaviors.mcu_base_behavior import McuBaseBehavior
from behaviors.mcu_mixer_screen_behavior import McuMixerScreenBehavior
from device_hal import mcu_buttons
from utilities import transliteration
from utilities.track_banking_manager import TrackBankingManager
from device_hal.mcu_device import McuDevice


class MixerRecButtonBehavior(McuBaseBehavior):
    """Behavior for handling REC button presses and updating REC button LEDs based on track arm status."""

    def __init__(self, mcuDevice: McuDevice, trackBankingManager: TrackBankingManager, screenBehavior: McuMixerScreenBehavior):
        super().__init__(mcuDevice)
        self.__trackBanking = trackBankingManager
        self.__screenBehavior = screenBehavior

    def OnEnable(self):
        super().OnEnable()
        self.__trackBanking.AddTrackChangeSubscriber(self._onTrackBankChange)

    def OnDisable(self):
        self.__trackBanking.RemoveTrackChangeSubscriber(self._onTrackBankChange)
        super().OnDisable()

    def _onTrackBankChange(self, newFirstTrack):
        """Called when track banking changes, update REC buttons."""
        self._updateRecButtons()

    def OnRefresh(self, flags):
        super().OnRefresh(flags)
        
        # Update REC button LEDs when mixer controls change
        if flags & midi.HW_Dirty_Mixer_Controls:
            self._updateRecButtons()

    def OnMidiMsg(self, event):
        """Handle REC button presses to arm/unarm tracks for recording in FL Studio mixer."""
        if event.midiId == midi.MIDI_NOTEON and event.data2 > 0:
            # Check if this is a REC button press
            if event.data1 in [mcu_buttons.Record_1, mcu_buttons.Record_2, mcu_buttons.Record_3, mcu_buttons.Record_4,
                               mcu_buttons.Record_5, mcu_buttons.Record_6, mcu_buttons.Record_7, mcu_buttons.Record_8]:
                # Calculate which track index was pressed
                rec_button_index = event.data1 - mcu_buttons.Record_1
                virtualTrackIndex = self.__trackBanking.GetTrackIndex(rec_button_index)
                
                assert virtualTrackIndex != -1, "Invalid track index for REC button press"
                # Only arm if the track exists in FL Studio
                if self.__trackBanking.VirtualTrackExists(virtualTrackIndex):
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
        virtualTrackIndexes = self.__trackBanking.GetTrackIndexes()
        
        for virtualIndex in virtualTrackIndexes:
            track = self.__trackBanking.GetHardwareTrack(virtualIndex)
            if track is not None and track.buttons is not None:
                # Determine if this track is armed
                isArmed = False
                if (self.__trackBanking.VirtualTrackExists(virtualIndex)):
                    isArmed = mixer.isTrackArmed(midi.TrackNum_Master + virtualIndex)
                track.buttons.SetArmButton(isArmed, isRecording)
