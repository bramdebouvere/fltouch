import general
import midi
import mixer

from utilities.fl_class_import import FlMidiMsg
from behaviors.mixer_banked_track_base_bahavior import MixerBankedTrackBaseBehavior
from device_hal import mcu_buttons
from device_hal import mcu_knob_mode
from utilities.track_banking_manager import TrackBankingManager
from device_hal.mcu_device import McuDevice
from constants import mcu_encoder
from utilities.encoder_resolution import CalculateMixerEncoderRes, CalculateEncoderMovementDelta

#TODO: add stereo message on the unit?

class MixerEncoderStereoBehavior(MixerBankedTrackBaseBehavior):
    """Behavior for synchronizing MCU encoder knobs with FL Studio mixer stereo separation values."""

    def __init__(self, mcuDevice: McuDevice, trackBankingManager: TrackBankingManager):
        super().__init__(mcuDevice, trackBankingManager)

    def Update(self):
        """
        Called from base class when the track bank changes or when tracks are marked dirty
        Updates stereo separation values on the MCU hw encoders.
        """
        trackIndexes = self.TrackBanking.GetTrackIndexes()

        for virtualIndex in trackIndexes:
            track = self.TrackBanking.GetHardwareTrack(virtualIndex)

            if track is not None and track.knob is not None:
                stereoValue = 0.5  # Default to center (0.5 is center, 0 is left, 1 is right)
                if self.TrackBanking.VirtualTrackExists(virtualIndex):
                    baseEventId = mixer.getTrackPluginId(virtualIndex, 0)
                    stereoEventId = baseEventId + midi.REC_Mixer_SS  # type: ignore
                    stereoValue = mixer.getEventValue(stereoEventId, midi.MaxInt, False)

                    # Convert FL Studio stereo separation value (0 - 1073741824) to knob position (1-6)
                    # Incoming FL Studio stereo value: 0 = super stereo, 1073741824 = fully merged
                    # We want: 1 = super stereo, 6 = merged
                    knobValue = 6 - round(stereoValue * (6 / midi.FromMIDI_Max))
                    
                    # Use Spread mode for stereo separation (center-positioned parameter)
                    track.knob.SetLedsValue(mcu_knob_mode.Spread, True, knobValue)
                else:
                    # Set to single dot mode with center led disabled, so no leds are lit
                    track.knob.SetLedsValue(mcu_knob_mode.SingleDot, False, 0)

    def OnMidiMsg(self, event: FlMidiMsg):
        """ Handle MIDI events for stereo separation encoders """

        # Handle encoder click to reset stereo separation to center
        if event.midiId == midi.MIDI_NOTEON and event.data2 > 0:
            if event.data1 in [mcu_buttons.Encoder_1, mcu_buttons.Encoder_2, mcu_buttons.Encoder_3,
                               mcu_buttons.Encoder_4, mcu_buttons.Encoder_5, mcu_buttons.Encoder_6,
                               mcu_buttons.Encoder_7, mcu_buttons.Encoder_8]:
                encoderIndex = event.data1 - mcu_buttons.Encoder_1
                virtualIndex = self.TrackBanking.GetTrackIndex(encoderIndex)
                if self.TrackBanking.VirtualTrackExists(virtualIndex):
                    # Reset stereo separation to center (= half of max value FromMIDI_Max)
                    baseEventId = mixer.getTrackPluginId(virtualIndex, 0)
                    stereoEventId = baseEventId + midi.REC_Mixer_SS  # type: ignore
                    mixer.automateEvent(stereoEventId, midi.FromMIDI_Max >> 1, midi.REC_MIDIController, 0)
                event.handled = True
                return event

        if event.midiId != midi.MIDI_CONTROLCHANGE:
            return super().OnMidiMsg(event)

        if event.midiChan != 0:
            return super().OnMidiMsg(event)

        # Handle encoder rotation (CC messages for encoders)
        # Encoder data format: data1 = 0x10 + encoder index, data2 = rotation value
        if mcu_encoder.EncoderCcBase <= event.data1 <= mcu_encoder.EncoderCcLast:
            encoderIndex = event.data1 - mcu_encoder.EncoderCcBase

            event.inEv = event.data2
            event.outEv = CalculateEncoderMovementDelta(event.data2)

            if encoderIndex < self.TrackBanking.TrackCount:
                virtualIndex = self.TrackBanking.GetTrackIndex(encoderIndex)
                if not self.TrackBanking.VirtualTrackExists(virtualIndex):
                    return super().OnMidiMsg(event)

                # Get stereo separation event id for the current track
                baseEventId = mixer.getTrackPluginId(virtualIndex, 0)
                stereoEventId = baseEventId + midi.REC_Mixer_SS  # type: ignore
                Res = CalculateMixerEncoderRes(event.outEv)
                
                mixer.automateEvent(stereoEventId, event.outEv, midi.REC_Controller, 0, 1, Res)

            event.handled = True
            return event

        return super().OnMidiMsg(event)
