# Shared, controller-driven state for the Effects mode's two sub-states.
#
# The Effects mode has two sub-states: a slot overview (the selected track's 10 effect slots) and a
# parameter view (one focused plugin's parameters). McuEffectsMode is the single writer of this object;
# the parameter behaviors are readers. It exists because the parameter behaviors are built once at mode
# construction, but the slot they operate on is only known when the user opens a plugin at runtime.
#
# The parameter view locks onto the plugin that was opened: its track, slot and plugin name are all
# captured on entry and the view keeps showing that plugin regardless of the live mixer selection. The
# captured plugin name lets the mode notice the opened plugin going away (removed or swapped) and leave.

# Sub-states
OVERVIEW = 0
PARAMS = 1
MENU = 2 # Flip menu (prev/next preset buttons)

class EffectsModeState:
    """Holds the active Effects sub-state and, when in the parameter view, the locked plugin's location."""

    def __init__(self):
        self.slot = -1          # effect slot shown in the parameter view (-1 = none / overview)
        self.track = -1         # mixer track the parameter view is locked to (-1 = none / overview)
        self.pluginName = ''    # captured name of the opened plugin, to detect it being removed/swapped
