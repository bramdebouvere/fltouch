import general
import midi
import mixer

from utilities.fl_class_import import FlMidiMsg
from behaviors.mixer_banked_track_base_bahavior import MixerBankedTrackBaseBehavior
from device_hal import mcu_buttons
from device_hal import mcu_knob_mode
from utilities.track_banking_manager import TrackBankingManager
from device_hal.mcu_device import McuDevice

#TODO: add panning message on the unit?

class MixerEncoderPanBehavior(MixerBankedTrackBaseBehavior):
    """Behavior for synchronizing MCU encoder knobs with FL Studio mixer pan values."""

    def __init__(self, mcuDevice: McuDevice, trackBankingManager: TrackBankingManager):
        super().__init__(mcuDevice, trackBankingManager)

    def Update(self):
        """
        Called from base class when the track bank changes or when tracks are marked dirty
        Updates pan values on the MCU hw encoders.
        """
        trackIndexes = self.TrackBanking.GetTrackIndexes()

        for virtualIndex in trackIndexes:
            track = self.TrackBanking.GetHardwareTrack(virtualIndex)

            if track is not None and track.knob is not None:
                panValue = 0.5  # Default to center (0.5 is center, 0 is left, 1 is right)
                if self.TrackBanking.VirtualTrackExists(virtualIndex):
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
                    # Set to single dot mode with center led disabled, so no leds are lit
                    track.knob.setLedsValue(mcu_knob_mode.SingleDot, False, 0)

    def OnMidiMsg(self, event: FlMidiMsg):
        """ Handle MIDI events for pan encoders """

        # Handle encoder click to reset pan to center
        if event.midiId == midi.MIDI_NOTEON and event.data2 > 0:
            if event.data1 in [mcu_buttons.Encoder_1, mcu_buttons.Encoder_2, mcu_buttons.Encoder_3,
                               mcu_buttons.Encoder_4, mcu_buttons.Encoder_5, mcu_buttons.Encoder_6,
                               mcu_buttons.Encoder_7, mcu_buttons.Encoder_8]:
                encoderIndex = event.data1 - mcu_buttons.Encoder_1
                virtualIndex = self.TrackBanking.GetTrackIndex(encoderIndex)
                if self.TrackBanking.VirtualTrackExists(virtualIndex):
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
                virtualIndex = self.TrackBanking.GetTrackIndex(encoderIndex)
                if not self.TrackBanking.VirtualTrackExists(virtualIndex):
                    return super().OnMidiMsg(event)

                # Determine pan delta based on encoder rotation
                panDelta = self.__getPanDeltaFromEncoderValue(event.data2)

                # Get pan event id for the current track
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

    def __getPanDeltaFromEncoderValue(self, value):
        # Convert MIDI CC value to pan delta
        # value: 0x40 = center, < 0x40 = left, > 0x40 = right
        if value >= 0x40:
            return (value - 0x40) / 64.0  # Right movement
        else:
            return (value - 0x40) / 64.0  # Left movement (negative)
