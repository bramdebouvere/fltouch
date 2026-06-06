import midi
import mixer

from utilities.fl_class_import import FlMidiMsg
from behaviors.mixer_banked_track_base_bahavior import MixerBankedTrackBaseBehavior
from device_hal import mcu_buttons
from utilities.track_banking_manager import TrackBankingManager
from device_hal.mcu_device import McuDevice
from device_hal.mcu_device_fader_conversion import McuFaderToFlFader

class MixerFaderBehavior(MixerBankedTrackBaseBehavior):
    """Behavior for synchronizing MCU faders with FL Studio mixer fader values."""

    def __init__(self, mcuDevice: McuDevice, trackBankingManager: TrackBankingManager):
        super().__init__(mcuDevice, trackBankingManager)

    def Update(self):
        """
        Called from base class when the track bank changes or when tracks are marked dirty
        Updates fader levels for all tracks in the current bank.
        """
        trackIndexes = self.TrackBanking.GetTrackIndexes()
        for virtualIndex in trackIndexes:
            sliderValue = 0
            if self.TrackBanking.VirtualTrackExists(virtualIndex):
                baseEventId = mixer.getTrackPluginId(virtualIndex, 0)
                sliderEventId = baseEventId + midi.REC_Mixer_Vol # type: ignore
                sliderValue = mixer.getEventValue(sliderEventId)

            track = self.TrackBanking.GetHardwareTrack(virtualIndex)
            if not track is None:
                track.fader.SetLevelFromFlsFader(sliderValue, False)

    def OnMidiMsg(self, event: FlMidiMsg):
        # Handle fader touch to select track
        if self.__isFaderTouchEvent(event):
            return self.__handleFaderTouchEvent(event)

        # Handle fader sliding
        if self.__isFaderSlideEvent(event):
            return self.__handleFaderSlideEvent(event)

        return super().OnMidiMsg(event)

    def __isFaderTouchEvent(self, event: FlMidiMsg):
        """ Detect if the MIDI event corresponds to a fader touch event on the MCU. """
        return event.midiId == midi.MIDI_NOTEON and event.data2 > 0 and event.data1 in [
            mcu_buttons.Slider_1, 
            mcu_buttons.Slider_2, 
            mcu_buttons.Slider_3, 
            mcu_buttons.Slider_4,
            mcu_buttons.Slider_5, 
            mcu_buttons.Slider_6, 
            mcu_buttons.Slider_7, 
            mcu_buttons.Slider_8, 
            mcu_buttons.Slider_Main
        ]
    
    def __handleFaderTouchEvent(self, event: FlMidiMsg):
        """ Handle fader touch events to select the corresponding track in FL Studio. """
        fader_index = event.data1 - mcu_buttons.Slider_1
        if fader_index < self.TrackBanking.TrackCount:
            virtualIndex = self.TrackBanking.GetTrackIndex(fader_index)
            if self.TrackBanking.VirtualTrackExists(virtualIndex):
                mixer.setTrackNumber(midi.TrackNum_Master + virtualIndex)
        #else:
            # Master fader touch event, could be used for something if desired, but not implemented for now
        event.handled = True
        return event
    
    def __isFaderSlideEvent(self, event: FlMidiMsg):
        """ Detect if the MIDI event corresponds to a fader slide event on the MCU. """
        return event.midiId == midi.MIDI_PITCHBEND and event.midiChan < (self.TrackBanking.TrackCount + 1)
    
    def __handleFaderSlideEvent(self, event: FlMidiMsg):
        """ Handle hw fader slide events to control the associated track in FL Studio. """
        event.inEv = event.data1 + (event.data2 << 7)
        event.outEv = (event.inEv << 16) // 16383
        event.inEv -= 0x2000

        flFaderValue = McuFaderToFlFader(event.inEv + 0x2000)
        if event.midiChan < self.TrackBanking.TrackCount:
            # Fader 1-8
            virtualIndex = self.TrackBanking.GetTrackIndex(event.midiChan)
            if not self.TrackBanking.VirtualTrackExists(virtualIndex):
                return super().OnMidiMsg(event)

            baseEventId = mixer.getTrackPluginId(virtualIndex, 0)
            sliderEventId = baseEventId + midi.REC_Mixer_Vol # type: ignore
            mixer.automateEvent(sliderEventId, flFaderValue, midi.REC_MIDIController, 0)
        else:
            # Main fader (does not control master fader, but main FL Studio volume)
            mixer.automateEvent(midi.REC_MainVol, flFaderValue, midi.REC_MIDIController, 0)

        event.handled = True
        return event
    