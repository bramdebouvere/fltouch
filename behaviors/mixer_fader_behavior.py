import general
import midi
import mixer

from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal import mcu_buttons
from device_hal import mcu_device_fader_conversion
from utilities.track_banking_manager import TrackBankingManager
from device_hal.mcu_device import McuDevice
from device_hal.mcu_device_fader_conversion import McuFaderToFlFader

class MixerFaderBehavior(McuBaseBehavior):
    """Behavior for synchronizing MCU faders with FL Studio mixer fader values."""

    def __init__(self, mcuDevice: McuDevice, trackBankingManager: TrackBankingManager):
        super().__init__(mcuDevice)
        self.__trackBanking = trackBankingManager
        self.__needsChanges = False


    def OnEnable(self):
        super().OnEnable()
        self.__trackBanking.AddTrackChangeSubscriber(self._onTrackBankChange)

    def OnDisable(self):
        self.__trackBanking.RemoveTrackChangeSubscriber(self._onTrackBankChange)
        super().OnDisable()

    def _onTrackBankChange(self, newFirstTrack):
        """Called when track banking changes, mark all tracks dirty to refresh faders."""
        self.__needsChanges = True
        self.OnDirtyMixerTrack(-1) # mark all tracks dirty to ensure faders are refreshed for new tracks in bank

    def OnDirtyMixerTrack(self, trackNum):
        """Track which mixer tracks are dirty so we can refresh faders on the next HW refresh."""
        if trackNum == -1:
            self.__needsChanges = True
            return

        trackIndexes = self.__trackBanking.GetTrackIndexes()
        if trackNum not in trackIndexes:
            return

        self.__needsChanges = True

    def OnRefresh(self, flags):
        super().OnRefresh(flags)

        if not (flags & midi.HW_Dirty_Mixer_Controls):
            return

        if not self.__needsChanges:
            return

        trackIndexes = self.__trackBanking.GetTrackIndexes()
        for virtualIndex in trackIndexes:
            sliderValue = 0
            if self.__trackBanking.VirtualTrackExists(virtualIndex):
                baseEventId = mixer.getTrackPluginId(virtualIndex, 0)
                sliderEventId = baseEventId + midi.REC_Mixer_Vol # type: ignore
                sliderValue = mixer.getEventValue(sliderEventId)

            track = self.__trackBanking.GetHardwareTrack(virtualIndex)
            if not track is None:
                track.fader.SetLevelFromFlsFader(sliderValue, False)

        self.__needsChanges = False

    def OnMidiMsg(self, event):
        if event.midiId == midi.MIDI_NOTEON and event.data2 > 0:
            # Handle fader touch to select track
            if event.data1 in [mcu_buttons.Slider_1, mcu_buttons.Slider_2, mcu_buttons.Slider_3, mcu_buttons.Slider_4,
                               mcu_buttons.Slider_5, mcu_buttons.Slider_6, mcu_buttons.Slider_7, mcu_buttons.Slider_8, mcu_buttons.Slider_Main]:
                fader_index = event.data1 - mcu_buttons.Slider_1
                if fader_index < 8:
                    trackIndexes = self.__trackBanking.GetTrackIndexes()
                    virtualIndex = trackIndexes[fader_index]
                    if self.__trackBanking.VirtualTrackExists(virtualIndex):
                        mixer.setTrackNumber(midi.TrackNum_Master + virtualIndex)
                #else:
                    # Master fader touch
                    #mixer.setTrackNumber(midi.TrackNum_Master)
                event.handled = True
                return event


        if event.midiId != midi.MIDI_PITCHBEND:
            return super().OnMidiMsg(event)

        if event.midiChan >= 8:
            return super().OnMidiMsg(event)

        event.inEv = event.data1 + (event.data2 << 7)
        event.outEv = (event.inEv << 16) // 16383
        event.inEv -= 0x2000

        flFaderValue = McuFaderToFlFader(event.inEv + 0x2000)
        if event.midiChan < 8:
            trackIndexes = self.__trackBanking.GetTrackIndexes()
            virtualIndex = trackIndexes[event.midiChan]
            if not self.__trackBanking.VirtualTrackExists(virtualIndex):
                return super().OnMidiMsg(event)

            baseEventId = mixer.getTrackPluginId(virtualIndex, 0)
            sliderEventId = baseEventId + midi.REC_Mixer_Vol # type: ignore
            mixer.automateEvent(sliderEventId, flFaderValue, midi.REC_MIDIController, 0)
        else:
            mixer.automateEvent(midi.REC_MainVol, flFaderValue, midi.REC_MIDIController, 0)

        event.handled = True
        return event

    def OnIdle(self):
        super().OnIdle();
