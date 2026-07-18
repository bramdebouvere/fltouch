import midi
import mixer
import plugins
import ui

from behaviors.mode_buttons_behavior import ModeButtonsBehavior
from behaviors.fader_touch_suppress_behavior import FaderTouchSuppressBehavior
from device_hal.mcu_device import McuDevice
from device_hal import mcu_buttons
from modes.mcu_composite_mode import McuCompositeMode
from modes.mcu_effect_slots_mode import McuEffectSlotsMode
from modes.mcu_effect_parameters_mode import McuEffectParametersMode
from utilities import effects_mode_state
from utilities.effects_mode_state import EffectsModeState
from utilities.track_banking_manager import TrackBankingManager

class McuEffectsMode(McuCompositeMode):
    """
    Effects mode: control the selected mixer track's effect plugins.

    Composed of two sub-modes:
    - McuEffectSlotsMode (OVERVIEW): browse and select effect slots.
    - McuEffectParametersMode (PARAMS): edit plugin parameters.
    """

    def __init__(self, device: McuDevice, slotBankingManager: TrackBankingManager, paramBankingManager: TrackBankingManager):
        self._state = EffectsModeState()
        super().__init__(device, [
            ModeButtonsBehavior(device, mcu_buttons.Effects),
            FaderTouchSuppressBehavior(device),
        ])

        # sub-modes
        slotMode = McuEffectSlotsMode(device, slotBankingManager, self)
        paramMode = McuEffectParametersMode(device, paramBankingManager, self._state, self)

        self._addSubMode(effects_mode_state.OVERVIEW, slotMode)
        self._addSubMode(effects_mode_state.PARAMS, paramMode)

    def OnEnable(self):
        if not self.McuDevice.isExtender:
            ui.showWindow(midi.widMixer)
            ui.setFocused(midi.widMixer)
        super().OnEnable()

    def OnModeSwitch(self, key, data):
        """
        Capture the target plugin's identity before the parameter sub-mode enables, or clear
        the state when returning to the slot overview. Implements base class.
        """
        if key == effects_mode_state.PARAMS:
            slot  = -1 if data is None else data
            track = mixer.trackNumber()
            self._state.slot = slot
            self._state.track = track
            self._state.pluginName = plugins.getPluginName(track, slot)
        else: # OVERVIEW
            # Close the effect plugin window the parameter view opened, if the slot still holds a plugin.
            # The mixer API has no hide-editor call (unlike channels.showCSForm), so we focus that plugin's
            # window and send Escape to close it - focusing first makes Escape target our plugin rather
            # than whatever else might be focused. Main unit drives FL windows.
            if (not self.McuDevice.isExtender and self._state.track >= 0 and self._state.slot >= 0
                    and mixer.isTrackPluginValid(self._state.track, self._state.slot)):
                mixer.focusEditor(self._state.track, self._state.slot)
                if ui.getFocused(midi.widPluginEffect): # make sure
                    ui.escape()
            self._state.slot = -1
            self._state.track = -1
            self._state.pluginName = ''
