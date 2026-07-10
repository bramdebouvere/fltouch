import midi
import mixer
import plugins

from behaviors.effects_param_screen_behavior import EffectsParamScreenBehavior
from behaviors.effects_param_encoder_behavior import EffectsParamEncoderBehavior
from behaviors.effects_param_select_button_behavior import EffectsParamSelectButtonBehavior
from behaviors.plugin_picker_button_behavior import PluginPickerButtonBehavior
from behaviors.track_banking_behavior import TrackBankingBehavior
from device_hal.mcu_device import McuDevice
from modes.mcu_base_mode import McuBaseMode
from utilities import effects_mode_state
from utilities.effects_mode_state import EffectsModeState
from utilities.effects_param_mapper import EffectsParamMapper
from utilities.track_banking_manager import TrackBankingManager


class McuEffectParametersMode(McuBaseMode):
    """
    Effects mode Parameter view sub-mode.

    Shows the opened plugin's parameters across the strips (banked through the parameter banking
    manager). Encoder = parameter value (press reverts to the value captured on entry), screen =
    parameter name + value. SELECT returns to the slot overview.

    The view is locked to the plugin captured in EffectsModeState by McuEffectsMode.OnModeSwitch.
    If the plugin is removed or swapped while this sub-mode is active the main unit detects it and
    requests a return to the slot overview (extenders follow via sync).
    """

    def __init__(self, device: McuDevice, paramBankingManager: TrackBankingManager,
                 state: EffectsModeState, compositeMode):
        self._state = state
        self._compositeMode = compositeMode
        super().__init__(device, [
            EffectsParamScreenBehavior(device, paramBankingManager, state),
            EffectsParamEncoderBehavior(device, paramBankingManager, state),
            TrackBankingBehavior(device, paramBankingManager),
            EffectsParamSelectButtonBehavior(device, compositeMode),
            PluginPickerButtonBehavior(device),
        ], paramBankingManager)

    def OnEnable(self):
        # Build the [virtual -> real] parameter map and size the banking to it before any behavior activates
        EffectsParamMapper.CreateMapForPlugin(self._state.track, self._state.slot)
        assert self._trackBankingManager is not None
        self._trackBankingManager.softwareTrackCount = len(EffectsParamMapper.Map)

        # enable behaviors + banking manager
        super().OnEnable() 

        # Always reset track banking
        self._trackBankingManager.SetFirstTrackIndex(0)

    def OnRefresh(self, flags):
        if not self._enabled:
            return
        
        # Main unit only: detect the locked plugin being removed or swapped; exit to overview.
        # Extenders follow via the sub-mode sync message that the main dispatches.
        if not self.McuDevice.isExtender:
            track = self._state.track
            slot = self._state.slot

            if not mixer.isTrackPluginValid(track, slot):
                self._compositeMode.SwitchTo(effects_mode_state.OVERVIEW)
                return
            
            # When the plugin name changes (plugin gets replaced), exit to overview
            if (flags & midi.HW_Dirty_Names) and plugins.getPluginName(track, slot) != self._state.pluginName:
                self._compositeMode.SwitchTo(effects_mode_state.OVERVIEW)
                return
            
        super().OnRefresh(flags)
