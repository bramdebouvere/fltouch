import midi
import mixer

from constants import mcu_constants
from datatypes.menu_item import MenuItem
from device_hal.mcu_colors import YellowColor, CyanColor

# The track-utility Flip menu for the mixer modes (Pan/Sends/Stereo). BuildMixerMenuItems() returns the
# items; each is bound to the live selected mixer track (mixer.trackNumber()), so no per-mode state is
# needed. getValue returns the bottom-row status text (OffOnStr[int(bool)] maps False/True -> 'off'/'on').

def _toggleCurrentTrackEffects(track):
    """Toggle all effect slots on/off for a single track."""
    mixer.enableTrackSlots(track, -1) # type: ignore # -1 = toggle
    mixer.afterRoutingChanged() # updates the FX-enable icon on the current track

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

def BuildMixerMenuItems() -> list[MenuItem]:
    """Track-utility Flip menu items, bound to the selected mixer track."""
    return [
        MenuItem('FxSlots', lambda: _toggleCurrentTrackEffects(mixer.trackNumber()), YellowColor, lambda: mcu_constants.OffOnStr[int(mixer.isTrackSlotsEnabled(mixer.trackNumber()))]),
        MenuItem('ALLFxSl', lambda: _toggleAllTrackEffects(mixer.trackNumber()),     YellowColor, lambda: mcu_constants.OffOnStr[int(_anyTrackEffectsEnabled())]),
        MenuItem('Rev Pol', lambda: _toggleTrackPolarity(mixer.trackNumber()),       CyanColor,   lambda: mcu_constants.OffOnStr[int(mixer.isTrackRevPolarity(mixer.trackNumber()))]),
        MenuItem('Swap LR', lambda: _toggleTrackChannelSwap(mixer.trackNumber()),    CyanColor,   lambda: mcu_constants.OffOnStr[int(mixer.isTrackSwapChannels(mixer.trackNumber()))]),
    ]
