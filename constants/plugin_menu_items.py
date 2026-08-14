import channels
import midi
import mixer
import plugins

from constants import mcu_constants
from datatypes.menu_item import MenuItem
from device_hal.mcu_colors import GreenColor, YellowColor
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

def _isTrackFree(track: int) -> bool:
    """Returns True if `track` has no effect plugins loaded and isn't already targeted by any channel,
    False otherwise."""
    for slot in range(mcu_constants.EffectsSlotCount):
        if mixer.isTrackPluginValid(track, slot):
            return False
    for channel in range(channels.channelCount(True)):
        if channels.getTargetFxTrack(channel, True) == track:
            return False
    return True

def _findFirstFreeTrack() -> int:
    """Returns the index of the first free mixer track after Master, or -1 if none are free."""
    for track in range(midi.TrackNum_Master + 1, mixer.trackCount()):
        if _isTrackFree(track):
            return track
    return -1

def _assignToSelectedTrack(state: ChannelRackModeState) -> None:
    """Routes the locked generator to the currently selected mixer track."""
    if state.channel >= 0 and plugins.isValid(state.channel, -1, True):
        channels.setTargetFxTrack(state.channel, mixer.trackNumber(), True)

def _assignToFirstFreeTrack(state: ChannelRackModeState) -> str | None:
    """
    Routes the locked generator to the first free mixer track. Returns a message to flash on screen
    if no free track exists, or None if the routing succeeded (or the guard failed) and there's nothing
    to report.
    """
    if state.channel < 0 or not plugins.isValid(state.channel, -1, True):
        return None
    track = _findFirstFreeTrack()
    if track == -1:
        return 'No free mixer track available'
    channels.setTargetFxTrack(state.channel, track, True)
    return None

def _currentTargetTrackStatus(state: ChannelRackModeState) -> str:
    """
    Returns the generator's current target track number as a string for the menu's status
    row, or '---' if there's no valid target to show.
    """
    if state.channel < 0:
        return '---'
    targetMixerTrackIndex = channels.getTargetFxTrack(state.channel, True)
    # Master (0) is the default/untouched target every channel starts with, not a meaningful
    # assignment, so it's treated the same as "no target" here (mirrors _findFirstFreeTrack, which
    # likewise never considers Master itself an assignable track).
    if not (midi.TrackNum_Master < targetMixerTrackIndex < mixer.trackCount()):
        return '---'
    return str(targetMixerTrackIndex)

def BuildGeneratorMenuItems(state: ChannelRackModeState) -> list[MenuItem]:
    """Plugin Flip menu items for the given ChannelRackModeState (bound to the locked generator)."""
    return [
        MenuItem('<Preset', lambda: _genPrevPreset(state), GreenColor),
        MenuItem('Preset>', lambda: _genNextPreset(state), GreenColor),
        MenuItem('AsToSel', lambda: _assignToSelectedTrack(state), YellowColor, lambda: _currentTargetTrackStatus(state)),
        MenuItem('AsToFre', lambda: _assignToFirstFreeTrack(state), YellowColor, lambda: _currentTargetTrackStatus(state)),
    ]
