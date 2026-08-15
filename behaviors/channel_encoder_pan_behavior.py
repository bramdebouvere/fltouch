import midi
import channels

from utilities.fl_class_import import FlMidiMsg
from behaviors.channel_banked_track_base_behavior import ChannelBankedTrackBaseBehavior
from device_hal import mcu_buttons
from device_hal import mcu_knob_mode
from utilities.track_banking_manager import TrackBankingManager
from device_hal.mcu_device import McuDevice
from constants import mcu_encoder
from constants.mcu_constants import ChannelPanRange
from utilities.encoder_resolution import CalculateMixerEncoderRes, CalculateEncoderMovementDelta

class ChannelEncoderPanBehavior(ChannelBankedTrackBaseBehavior):
    """Behavior for synchronizing MCU encoder knobs with channel-rack channel pan values."""

    def __init__(self, mcuDevice: McuDevice, trackBankingManager: TrackBankingManager):
        super().__init__(mcuDevice, trackBankingManager)

    def OnDisable(self):
        
        super().OnDisable()
        self.McuDevice.ClearEncoderRings()

    def Update(self):
        """Update pan values on the MCU hw encoder rings for the current bank."""
        for virtualIndex in self.TrackBanking.GetTrackIndexes():
            track = self.TrackBanking.GetHardwareTrack(virtualIndex)
            if track is None or track.knob is None:
                continue

            if self.TrackBanking.VirtualTrackExists(virtualIndex):
                pan = channels.getChannelPan(virtualIndex, True) # -1.0 .. 1.0, global index
                track.knob.SetLedsValue(mcu_knob_mode.BoostCut, True, self.__panToKnobValue(pan))
            else:
                # No leds lit for strips beyond the available channels
                track.knob.SetLedsValueNone()

    def OnMidiMsg(self, event: FlMidiMsg):
        # Encoder click resets pan to center
        if event.midiId == midi.MIDI_NOTEON and event.data2 > 0:
            if mcu_buttons.Encoder_1 <= event.data1 <= mcu_buttons.Encoder_8:
                encoderIndex = event.data1 - mcu_buttons.Encoder_1
                virtualIndex = self.TrackBanking.GetTrackIndex(encoderIndex)
                if self.TrackBanking.VirtualTrackExists(virtualIndex):
                    channels.setChannelPan(virtualIndex, 0.0, useGlobalIndex=True)
                event.handled = True
                return event

        if event.midiId != midi.MIDI_CONTROLCHANGE or event.midiChan != 0:
            return super().OnMidiMsg(event)

        # Encoder rotation: data1 = 0x10 + encoder index, data2 = relative rotation value
        if mcu_encoder.EncoderCcBase <= event.data1 <= mcu_encoder.EncoderCcLast:
            encoderIndex = event.data1 - mcu_encoder.EncoderCcBase

            if encoderIndex < self.TrackBanking.TrackCount:
                virtualIndex = self.TrackBanking.GetTrackIndex(encoderIndex)
                if not self.TrackBanking.VirtualTrackExists(virtualIndex):
                    return super().OnMidiMsg(event)

                # steps > 0 = clockwise/right, steps < 0 = counter-clockwise/left.
                steps = CalculateEncoderMovementDelta(event.data2)
                res = CalculateMixerEncoderRes(steps)
                current = channels.getChannelPan(virtualIndex, True)
                newPan = max(-1.0, min(1.0, current + steps * res * ChannelPanRange))
                channels.setChannelPan(virtualIndex, newPan, useGlobalIndex=True)

                # Reflect the new value on the ring right away (FL may not echo a refresh for our own change).
                track = self.TrackBanking.GetHardwareTrack(virtualIndex)
                if track is not None and track.knob is not None:
                    track.knob.SetLedsValue(mcu_knob_mode.BoostCut, True, self.__panToKnobValue(newPan))

            event.handled = True
            return event

        return super().OnMidiMsg(event)

    def __panToKnobValue(self, pan: float) -> int:
        """Convert a -1.0 .. 1.0 pan value to a ring position (1 = left, 6 = center, 11 = right)."""
        knobValue = 1 + round((pan + 1.0) / ChannelPanRange * 10)
        return max(1, min(11, knobValue))
