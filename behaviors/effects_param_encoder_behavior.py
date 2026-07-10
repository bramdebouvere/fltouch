import midi
import mixer
import plugins

from utilities.fl_class_import import FlMidiMsg
from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal import mcu_buttons
from device_hal import mcu_knob_mode
from device_hal.mcu_device import McuDevice
from utilities.track_banking_manager import TrackBankingManager
from utilities.effects_mode_state import EffectsModeState
from utilities.effects_param_mapper import EffectsParamMapper
from constants import mcu_encoder
from utilities.encoder_resolution import CalculateParamEncoderRes, CalculateEncoderMovementDelta

class EffectsParamEncoderBehavior(McuBaseBehavior):
    """
    Controls the opened plugin's parameters with the rotary encoders.

    A virtual index handed out by the TrackBankingManager is translated to an FL parameter index through
    EffectsParamMapper.Map, so the encoders spread across and bank through the plugin's real, named
    parameters only. The target plugin is the track + slot the view locked onto when it was opened
    (EffectsModeState), not the live mixer selection.

    Encoder click reverts a parameter to the value it had when the parameter view was entered: a snapshot
    (indexed by virtual parameter) is captured on enable (FL exposes no per-parameter factory default).
    """

    def __init__(self, mcuDevice: McuDevice, trackBankingManager: TrackBankingManager, state: EffectsModeState):
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

        track = self.__state.track
        slot = self.__state.slot

        if track >= 0 and slot >= 0 and mixer.isTrackPluginValid(track, slot):
            self.Update()

    def OnRefresh(self, flags):
        super().OnRefresh(flags)

        # Plugin parameter values report changes via HW_Dirty_ControlValues (mixer events like pan/EQ use
        # HW_Dirty_Mixer_Controls instead, hence both). The view is locked to its plugin, so a mixer
        # selection change is not a trigger and the snapshot stays put (re-captured only on OnEnable).
        if flags & (midi.HW_Dirty_ControlValues | midi.HW_Dirty_Mixer_Controls):
            self.Update()

    def __captureSnapshot(self):
        """
        Record each mapped parameter's current value so encoder clicks can revert to it (since otherwisse there is no "default" to return to).
        """
        track = self.__state.track
        slot = self.__state.slot

        if track < 0 or slot < 0 or not mixer.isTrackPluginValid(track, slot):
            self.__snapshot = []
            return
        
        m = EffectsParamMapper.Map
        self.__snapshot = [plugins.getParamValue(m[v], track, slot) for v in range(len(m))]

    def Update(self):
        """Update the encoder rings to reflect each banked parameter's normalized value."""
        track = self.__state.track
        slot = self.__state.slot
        valid = track >= 0 and slot >= 0 and mixer.isTrackPluginValid(track, slot)

        for virtualIndex in self.__trackBanking.GetTrackIndexes():
            hwTrack = self.__trackBanking.GetHardwareTrack(virtualIndex)
            if hwTrack is None or hwTrack.knob is None:
                continue

            if not (valid and self.__trackBanking.VirtualTrackExists(virtualIndex)):
                hwTrack.knob.SetLedsValue(mcu_knob_mode.SingleDot, False, 0)
                continue

            value = plugins.getParamValue(EffectsParamMapper.Map[virtualIndex], track, slot)  # normalized 0.0 - 1.0
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
            track = self.__state.track
            slot = self.__state.slot
            
            if (self.__trackBanking.VirtualTrackExists(virtualIndex)
                    and track >= 0 and slot >= 0 and mixer.isTrackPluginValid(track, slot)):
                realIndex = EffectsParamMapper.Map[virtualIndex]
                current = plugins.getParamValue(realIndex, track, slot)
                # Variable step: very fine when turning slowly, accelerating as you spin faster.
                res = CalculateParamEncoderRes(steps)
                newValue = max(0.0, min(1.0, current + steps * res))
                plugins.setParamValue(newValue, realIndex, track, slot)

                # Reflect the new value on the ring right away (FL may not echo a refresh for our own change).
                hwTrack = self.__trackBanking.GetHardwareTrack(virtualIndex)
                if hwTrack is not None and hwTrack.knob is not None:
                    hwTrack.knob.SetLedsValue(mcu_knob_mode.Wrap, False, max(0, min(11, round(newValue * 11))))

            event.handled = True
            return event

        return super().OnMidiMsg(event)

    def __resetParam(self, virtualIndex):
        """Revert the parameter to its value when the parameter view was entered (snapshot)."""
        track = self.__state.track
        slot = self.__state.slot

        if not self.__trackBanking.VirtualTrackExists(virtualIndex):
            return
        if track < 0 or slot < 0 or not mixer.isTrackPluginValid(track, slot):
            return
        
        if 0 <= virtualIndex < len(self.__snapshot):
            plugins.setParamValue(self.__snapshot[virtualIndex], EffectsParamMapper.Map[virtualIndex], track, slot)
