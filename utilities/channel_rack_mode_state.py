# Shared, controller-driven state for the Channel Rack mode's two sub-states.
#
# The Channel Rack mode has two sub-states: a channel overview (all channels, with volume/pan/mute/solo
# per strip) and a parameter view (one focused generator's plugin parameters). McuChannelRackMode is the
# single writer of this object; the parameter behaviors are readers.

# Sub-states
OVERVIEW = 0
PARAMS = 1

class ChannelRackModeState:
    """Holds the active Channel Rack sub-state and, when in the parameter view, the locked generator's channel."""

    def __init__(self):
        self.channel = -1 # global channel index the parameter view is locked to (-1 = none / overview)
        self.pluginName = '' # captured name of the opened generator, to detect it being removed/swapped
