import midi
import mixer

from constants import mcu_constants

# Shared definitions for the Flip menu's track utility functions.
#
# A TrackBankingManager indexes straight into the MENU_ITEMS list below

_YELLOW = 0xFFC000
_CYAN = 0x478C8D

def _toggleCurrentTrackEffects(track):
    """Toggle all effect slots on/off for a single track."""
    mixer.enableTrackSlots(track, -1)  # type: ignore # -1 = toggle
    mixer.afterRoutingChanged()  # updates the FX-enable icon on the current track

def _anyTrackEffectsEnabled():
    """Returns True if any track has its effect slots enabled, False otherwise."""
    firstTrack = midi.TrackNum_Master + 1 # skip the master track
    return any(mixer.isTrackSlotsEnabled(t) for t in range(firstTrack, mixer.trackCount()))

def _trackHasPlugin(track):
    """Returns True if the track has a valid plugin in any slot, False otherwise."""
    return any(mixer.isTrackPluginValid(track, slot) for slot in range(mcu_constants.EffectsSlotCount))

def _toggleAllTrackEffects(track):
    """Toggle all effect slots on/off for every track (mirrors the old Shift+Flip behavior)."""
    firstTrack = midi.TrackNum_Master + 1
    enable = not _anyTrackEffectsEnabled()
    originalTrack = mixer.trackNumber()

    # FL Bug workaround:
    #  FL Studio only repaints a track's FX-enable icon while that track is the current mixer track, so
    #  briefly select each track with a plugin to force its icon to recompute, then restore the selection.
    for t in range(firstTrack, mixer.trackCount()):
        mixer.enableTrackSlots(t, enable)
        if _trackHasPlugin(t):
            mixer.setTrackNumber(t)

    mixer.setTrackNumber(originalTrack)
    mixer.afterRoutingChanged()

def _toggleTrackPolarity(track):
    # revTrackPolarity(track) alone would set polarity to False rather than toggle it, so the negated
    # current state is always passed explicitly.
    mixer.revTrackPolarity(track, not mixer.isTrackRevPolarity(track)) 

def _toggleTrackChannelSwap(track):
    # Same known issue as revTrackPolarity: swapTrackChannels(track) alone sets it to False.
    mixer.swapTrackChannels(track, not mixer.isTrackSwapChannels(track)) 

#   'label'    : scribble-strip label
#   'execute'  : fn(track) -> None, runs the action
#   'getValue' : optional fn(track) -> bool, the current on/off state shown on the bottom row.
#                Omit for a plain action with no on/off state to show (bottom row stays blank).
#   'color'    : FL color int for the scribble strip
MENU_ITEMS = [
    {'label': 'FxSlots', 'execute': _toggleCurrentTrackEffects, 'getValue': mixer.isTrackSlotsEnabled,               'color': _YELLOW},
    {'label': 'ALLFxSl', 'execute': _toggleAllTrackEffects,     'getValue': lambda track: _anyTrackEffectsEnabled(), 'color': _YELLOW},
    {'label': 'Rev Pol', 'execute': _toggleTrackPolarity,       'getValue': mixer.isTrackRevPolarity,                'color': _CYAN},
    {'label': 'Swap LR', 'execute': _toggleTrackChannelSwap,    'getValue': mixer.isTrackSwapChannels,               'color': _CYAN},
]

# Number of menu items
MenuItemCount = len(MENU_ITEMS)

def GetMenuItemLabel(virtualIndex):
    """The scribble-strip label for a menu item index."""
    return MENU_ITEMS[virtualIndex]['label']

def ExecuteMenuItem(virtualIndex, track):
    """Runs a menu item's action against the given mixer track."""
    MENU_ITEMS[virtualIndex]['execute'](track)

def GetMenuItemValue(virtualIndex, track):
    """The current on/off state of a menu item for the given mixer track, or None if the item is a
    plain action with no on/off state (no 'getValue' provided)."""
    getValue = MENU_ITEMS[virtualIndex].get('getValue')
    return None if getValue is None else getValue(track)

def GetMenuItemColor(virtualIndex):
    """The FL Studio color int for a menu item index."""
    return MENU_ITEMS[virtualIndex]['color']
