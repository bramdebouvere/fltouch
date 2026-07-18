import midi
import channels
import general
import plugins

from utilities.fl_class_import import FlMidiMsg
from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal import mcu_buttons
from device_hal import mcu_knob_mode
from device_hal.mcu_device import McuDevice
from utilities.track_banking_manager import TrackBankingManager
from utilities.channel_rack_mode_state import ChannelRackModeState
from utilities.channel_param_mapper import ChannelParamMapper
from constants import mcu_encoder
from utilities.encoder_resolution import CalculateParamEncoderRes, CalculateEncoderMovementDelta

class ChannelParamEncoderBehavior(McuBaseBehavior):
    """
    Controls the opened generator's parameters with the rotary encoders.

    A virtual index handed out by the TrackBankingManager is translated to an FL parameter index through
    ChannelParamMapper.Map, so the encoders spread across and bank through the generator's real, named
    parameters only. The target generator is the channel the view locked onto when it was opened
    (ChannelRackModeState), not the live channel selection.

    Encoder click reverts a parameter to the value it had when the parameter view was entered: a snapshot
    (indexed by virtual parameter) is captured on enable (FL exposes no per-parameter factory default).
    """

    def __init__(self, mcuDevice: McuDevice, trackBankingManager: TrackBankingManager, state: ChannelRackModeState):
        super().__init__(mcuDevice)
        self.__trackBanking = trackBankingManager
        self.__state = state
        self.__snapshot = []

    def OnEnable(self):
        super().OnEnable()
        self.__trackBanking.AddTrackChangeSubscriber(self.__onTrackBankChange)
        self.__captureSnapshot()
        self.Update()

    def OnDisable(self):
        self.__trackBanking.RemoveTrackChangeSubscriber(self.__onTrackBankChange)
        self.McuDevice.ClearEncoderRings()
        super().OnDisable()

    def __onTrackBankChange(self, newFirstTrack):
        self.Update()

    def OnIdle(self):
        super().OnIdle()
        if self.__isChannelValid():
            self.Update()

    def OnRefresh(self, flags):
        super().OnRefresh(flags)

        # Plugin parameter values report changes via HW_Dirty_ControlValues; also refresh on channel events.
        if flags & (midi.HW_Dirty_ControlValues | midi.HW_ChannelEvent):
            self.Update()

    def __isChannelValid(self):
        channel = self.__state.channel
        return channel >= 0 and channel < channels.channelCount(True)

    def __captureSnapshot(self):
        """Record each mapped parameter's current value so encoder clicks can revert to it."""
        if not self.__isChannelValid():
            self.__snapshot = []
            return

        channel = self.__state.channel
        m = ChannelParamMapper.Map
        self.__snapshot = [plugins.getParamValue(m[v], channel, -1, True) for v in range(len(m))]

    def Update(self):
        """Update the encoder rings to reflect each banked parameter's normalized value."""
        valid = self.__isChannelValid()
        channel = self.__state.channel

        for virtualIndex in self.__trackBanking.GetTrackIndexes():
            hwTrack = self.__trackBanking.GetHardwareTrack(virtualIndex)
            if hwTrack is None or hwTrack.knob is None:
                continue

            if not (valid and self.__trackBanking.VirtualTrackExists(virtualIndex)):
                hwTrack.knob.SetLedsValue(mcu_knob_mode.SingleDot, False, 0)
                continue

            value = plugins.getParamValue(ChannelParamMapper.Map[virtualIndex], channel, -1, True) # normalized 0.0 - 1.0
            ledValue = max(0, min(mcu_encoder.LedWrapMax, round(value * mcu_encoder.LedWrapMax)))
            hwTrack.knob.SetLedsValue(mcu_knob_mode.Wrap, False, ledValue)

    def OnMidiMsg(self, event: FlMidiMsg):
        # Encoder click -> revert the parameter to its opened-state snapshot value
        if event.midiId == midi.MIDI_NOTEON and event.data2 > 0:
            if mcu_buttons.Encoder_1 <= event.data1 <= mcu_buttons.Encoder_8:
                encoderIndex = event.data1 - mcu_buttons.Encoder_1
                virtualIndex = self.__trackBanking.GetTrackIndex(encoderIndex)
                self.__resetParam(virtualIndex)
                event.handled = True
                return event

        if event.midiId != midi.MIDI_CONTROLCHANGE:
            return super().OnMidiMsg(event)
        if event.midiChan != 0:
            return super().OnMidiMsg(event)

        # Encoder rotation: data1 = 0x10 + encoder index, data2 = relative rotation value
        if mcu_encoder.EncoderCcBase <= event.data1 <= mcu_encoder.EncoderCcLast:
            encoderIndex = event.data1 - mcu_encoder.EncoderCcBase

            steps = CalculateEncoderMovementDelta(event.data2)

            virtualIndex = self.__trackBanking.GetTrackIndex(encoderIndex)
            channel = self.__state.channel

            if self.__trackBanking.VirtualTrackExists(virtualIndex) and self.__isChannelValid():
                realIndex = ChannelParamMapper.Map[virtualIndex]

                # Get eventId for the parameter
                eventId = channels.getRecEventId(channel, True) + midi.REC_Chan_Plugin_First + realIndex  # type: ignore
                # res sets the per-detent granularity for continuous params (fine, accelerating on
                # faster turns); FL ignores it for discrete params, stepping those one value per detent.
                res = CalculateParamEncoderRes(steps)
                newValue = channels.incEventValue(eventId, steps, res)
                general.processRECEvent(eventId, newValue, midi.REC_UpdateValue | midi.REC_UpdateControl)

                # Reflect the applied value on the ring right away (FL may not echo a refresh for our own change).
                hwTrack = self.__trackBanking.GetHardwareTrack(virtualIndex)
                if hwTrack is not None and hwTrack.knob is not None:
                    value = plugins.getParamValue(realIndex, channel, -1, True) # normalized 0.0 - 1.0
                    ledValue = max(0, min(mcu_encoder.LedWrapMax, round(value * mcu_encoder.LedWrapMax)))
                    hwTrack.knob.SetLedsValue(mcu_knob_mode.Wrap, False, ledValue)

            event.handled = True
            return event

        return super().OnMidiMsg(event)

    def __resetParam(self, virtualIndex):
        """Revert the parameter to its value when the parameter view was entered (snapshot)."""
        if not self.__trackBanking.VirtualTrackExists(virtualIndex):
            return
        if not self.__isChannelValid():
            return

        if 0 <= virtualIndex < len(self.__snapshot):
            plugins.setParamValue(self.__snapshot[virtualIndex], ChannelParamMapper.Map[virtualIndex], self.__state.channel, -1, useGlobalIndex=True)
