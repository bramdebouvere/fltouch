import general
import midi
import mixer

from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal import mcu_buttons
from device_hal import mcu_knob_mode
from utilities.track_banking_manager import TrackBankingManager
from device_hal.mcu_device import McuDevice

#TODO: clean this code up a little bit in separate functions
#TODO: add BankedMixerBehavior to handle bank switching and then have this behavior only handle the encoder<->pan synchronization. All other mixer banked behavior should also use the same base class
#TODO: add panning message on the unit?

class MixerEncoderPanBehavior(McuBaseBehavior):
    """Behavior for synchronizing MCU encoder knobs with FL Studio mixer pan values."""

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
        """Called when track banking changes, mark all tracks dirty to refresh encoders."""
        self.__needsChanges = True
        self.OnDirtyMixerTrack(-1)  # mark all tracks dirty to ensure knobs are refreshed for new tracks in bank

    def OnDirtyMixerTrack(self, trackNum):
        """Track which mixer tracks are dirty so we can refresh encoders on the next HW refresh."""
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
            
            track = self.__trackBanking.GetHardwareTrack(virtualIndex)
            if track is not None and track.knob is not None:

                panValue = 0.5  # Default to center (0.5 is center, 0 is left, 1 is right)
                if self.__trackBanking.VirtualTrackExists(virtualIndex):
                    baseEventId = mixer.getTrackPluginId(virtualIndex, 0)
                    panEventId = baseEventId + midi.REC_Mixer_Pan  # type: ignore
                    panValue = mixer.getEventValue(panEventId, midi.MaxInt, False)

                    # Convert FL Studio pan value (0-1073741824) to knob position (1-11)
                    # Incoming FL Studio pan value: 0 = full left, 1073741824 = full right
                    # We want: 1 = left, 6 = center, 11 = right (0 = all leds in ring off, 1-5 = left side leds, 6 = center led, 7-11 = right side leds)
                    knobValue = 1 + round(panValue * (10 / midi.FromMIDI_Max))
                    
                    # Use BoostCut mode for pan (center-positioned parameter)
                    track.knob.setLedsValue(mcu_knob_mode.BoostCut, True, knobValue)
                else:
                    track.knob.setLedsValue(mcu_knob_mode.SingleDot, False, 0)

        self.__needsChanges = False

    def OnMidiMsg(self, event):
        if event.midiId == midi.MIDI_NOTEON and event.data2 > 0:
            # Handle encoder click to reset pan to center
            if event.data1 in [mcu_buttons.Encoder_1, mcu_buttons.Encoder_2, mcu_buttons.Encoder_3,
                               mcu_buttons.Encoder_4, mcu_buttons.Encoder_5, mcu_buttons.Encoder_6,
                               mcu_buttons.Encoder_7, mcu_buttons.Encoder_8]:
                encoderIndex = event.data1 - mcu_buttons.Encoder_1
                trackIndexes = self.__trackBanking.GetTrackIndexes()
                virtualIndex = trackIndexes[encoderIndex]
                if self.__trackBanking.VirtualTrackExists(virtualIndex):
                    # Reset pan to center (= half of max value FromMIDI_Max)
                    baseEventId = mixer.getTrackPluginId(virtualIndex, 0)
                    panEventId = baseEventId + midi.REC_Mixer_Pan  # type: ignore
                    mixer.automateEvent(panEventId, midi.FromMIDI_Max >> 1, midi.REC_MIDIController, 0)
                event.handled = True
                return event

        if event.midiId != midi.MIDI_CONTROLCHANGE:
            return super().OnMidiMsg(event)

        if event.midiChan != 0:
            return super().OnMidiMsg(event)

        # Handle encoder rotation (CC messages for encoders)
        # Encoder data format: data1 = 0x10 + encoder index, data2 = rotation value
        if event.data1 in [0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17]:
            encoderIndex = event.data1 - 0x10

            event.inEv = event.data2
            if event.inEv >= 0x40:
                event.outEv = -(event.inEv - 0x40)
            else:
                event.outEv = event.inEv

            if encoderIndex < 8:
                virtualIndex = self.__trackBanking.GetTrackIndex(encoderIndex)
                if not self.__trackBanking.VirtualTrackExists(virtualIndex):
                    return super().OnMidiMsg(event)

                # Convert MIDI CC value to pan delta
                # data2 value: 0x40 = center, < 0x40 = left, > 0x40 = right
                if event.data2 >= 0x40:
                    panDelta = (event.data2 - 0x40) / 64.0  # Right movement
                else:
                    panDelta = (event.data2 - 0x40) / 64.0  # Left movement (negative)

                baseEventId = mixer.getTrackPluginId(virtualIndex, 0)
                panEventId = baseEventId + midi.REC_Mixer_Pan  # type: ignore
                
                # Get current pan value and add delta
                currentPan = mixer.getEventValue(panEventId)
                newPan = currentPan + panDelta
                newPan = max(0, min(1, newPan))  # Clamp to 0-1
                Res = 0.005 + ((abs(event.outEv)-1) / 2000)
                
                mixer.automateEvent(panEventId, event.outEv, midi.REC_Controller, 0, 1, Res)

            event.handled = True
            return event

        return super().OnMidiMsg(event)

    def OnIdle(self):
        super().OnIdle()
