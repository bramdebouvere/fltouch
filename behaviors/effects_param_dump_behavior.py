import midi
import plugins

from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal import mcu_buttons
from device_hal.mcu_device import McuDevice
from utilities.button_manager import ButtonManager
from utilities.effects_mode_state import EffectsModeState
from utilities.effects_param_mapper import EffectsParamMapper
from utilities.plugin_param_config import PluginParamConfig

class EffectsParamDumpBehavior(McuBaseBehavior):
    """
    Shift+Record_1 dumps the opened generator's current plugin parameters to FL's script output console as JSON,
    so a new config can be made by copying the output, reordering entries and adding colors.

    This allows users to create a custom config for plugins (reordering and coloring parameters).
    """

    def __init__(self, mcuDevice: McuDevice, state: EffectsModeState):
        super().__init__(mcuDevice)
        self._state = state

    def OnMidiMsg(self, event):
        if event.midiId != midi.MIDI_NOTEON:
            return super().OnMidiMsg(event)
        if event.data1 != mcu_buttons.Record_1:
            return super().OnMidiMsg(event)

        if event.data2 > 0 and ButtonManager.ShiftPressed:
            self._Dump()

        event.handled = True
        return event

    def _Dump(self):
        track = self._state.track
        slot = self._state.slot
        pluginName = self._state.pluginName
        if track < 0 or slot < 0:
            return

        entries: list[tuple[int, str, int | None]] = []
        for index in EffectsParamMapper.Map:
            name = plugins.getParamName(index, track, slot)
            color = PluginParamConfig.GetColor(pluginName, index)
            entries.append((index, name, color))

        PluginParamConfig.DumpCurrentParameterList(pluginName, entries)
