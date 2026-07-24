import mixer
import plugins

from datatypes.menu_item import MenuItem
from device_hal.mcu_colors import GreenColor
from utilities.channel_rack_mode_state import ChannelRackModeState
from utilities.effects_mode_state import EffectsModeState

# Flip menus for the plugin parameter views (Effects mode's FX plugins and Channel Rack mode's generators).
# Currently just preset stepping, but this is where further per-plugin actions would go.

# Mixer FX plugins

def _fxPrevPreset(state: EffectsModeState):
    if state.track >= 0 and state.slot >= 0 and mixer.isTrackPluginValid(state.track, state.slot):
        plugins.prevPreset(state.track, state.slot)
        state.pluginName = plugins.getPluginName(state.track, state.slot)

def _fxNextPreset(state: EffectsModeState):
    if state.track >= 0 and state.slot >= 0 and mixer.isTrackPluginValid(state.track, state.slot):
        plugins.nextPreset(state.track, state.slot)
        state.pluginName = plugins.getPluginName(state.track, state.slot)

def BuildEffectMenuItems(state: EffectsModeState) -> list[MenuItem]:
    """Plugin Flip menu items for the given EffectsModeState (bound to the locked mixer FX plugin)."""
    return [
        MenuItem('<Preset', lambda: _fxPrevPreset(state), GreenColor),
        MenuItem('Preset>', lambda: _fxNextPreset(state), GreenColor),
    ]

# Channel Rack generators

def _genPrevPreset(state: ChannelRackModeState):
    if state.channel >= 0 and plugins.isValid(state.channel, -1, True):
        plugins.prevPreset(state.channel, -1, True)
        state.pluginName = plugins.getPluginName(state.channel, -1, False, True)

def _genNextPreset(state: ChannelRackModeState):
    if state.channel >= 0 and plugins.isValid(state.channel, -1, True):
        plugins.nextPreset(state.channel, -1, True)
        state.pluginName = plugins.getPluginName(state.channel, -1, False, True)

def BuildGeneratorMenuItems(state: ChannelRackModeState) -> list[MenuItem]:
    """Plugin Flip menu items for the given ChannelRackModeState (bound to the locked generator)."""
    return [
        MenuItem('<Preset', lambda: _genPrevPreset(state), GreenColor),
        MenuItem('Preset>', lambda: _genNextPreset(state), GreenColor),
    ]
