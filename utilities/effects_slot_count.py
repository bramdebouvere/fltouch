import mixer

from constants import mcu_constants

def GetEffectsSlotCount(track: int) -> int:
    """
    Returns the number of effect slots on the given mixer track.

    Since FL Studio 2026.2, each track can have a different number of
    slots (1..25, grown on demand). Before 26.2 the count was fixed at 10.
    """
    if not hasattr(mixer, 'getSlotCount'):
        return mcu_constants.EffectsSlotCount

    try:
        return mixer.getSlotCount(track) # type: ignore
    except RuntimeError:
        # FL can throw "Index out of range" for track indexes that don't exist
        return mcu_constants.EffectsSlotCount
