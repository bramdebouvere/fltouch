import midi
import mixer

from behaviors.mcu_base_behavior import McuBaseBehavior
from behaviors.mixer_banked_track_base_bahavior import MixerBankedTrackBaseBehavior
from device_hal import mcu_buttons
from utilities.track_banking_manager import TrackBankingManager
from device_hal.mcu_device import McuDevice


class MixerSelectButtonBehavior(MixerBankedTrackBaseBehavior):
    """Behavior for handling select button presses and updating select button LEDs based on track selection."""

    def __init__(self, mcuDevice: McuDevice, trackBankingManager: TrackBankingManager):
        super().__init__(mcuDevice, trackBankingManager, midi.HW_Dirty_Mixer_Sel)

    def Update(self):
        """ Called by base class when track banking changes or when tracks are marked dirty, updates select buttons. """
        self._updateSelectButtons()

    def OnMidiMsg(self, event):
        """Handle select button presses to select tracks in FL Studio mixer."""
        if event.midiId == midi.MIDI_NOTEON and event.data2 > 0:
            # Check if this is a select button press
            if event.data1 in [mcu_buttons.Select_1, mcu_buttons.Select_2, mcu_buttons.Select_3, mcu_buttons.Select_4,
                               mcu_buttons.Select_5, mcu_buttons.Select_6, mcu_buttons.Select_7, mcu_buttons.Select_8]:
                # Calculate which track index was pressed
                select_button_index = event.data1 - mcu_buttons.Select_1
                virtualTrackIndex = self.TrackBanking.GetTrackIndex(select_button_index)
                
                assert virtualTrackIndex != -1, "Invalid track index for select button press"
                # Only select if the track exists in FL Studio
                if self.TrackBanking.VirtualTrackExists(virtualTrackIndex):
                    mixer.setTrackNumber(midi.TrackNum_Master + virtualTrackIndex)
                
                event.handled = True
                return event

    def _updateSelectButtons(self):
        """Update all select button LEDs to reflect current track selection."""
        currentTrackNum = mixer.trackNumber()
        virtualTrackIndexes = self.TrackBanking.GetTrackIndexes()
        
        for virtualIndex in virtualTrackIndexes:
            track = self.TrackBanking.GetHardwareTrack(virtualIndex)
            if track is not None and track.buttons is not None:
                # Determine if this track is selected
                isSelected = False
                if (self.TrackBanking.VirtualTrackExists(virtualIndex)):
                    isSelected = (midi.TrackNum_Master + virtualIndex) == currentTrackNum
                track.buttons.SetSelectButton(isSelected)
