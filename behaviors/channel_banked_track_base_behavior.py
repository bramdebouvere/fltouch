import midi

from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal.mcu_device import McuDevice
from utilities.track_banking_manager import TrackBankingManager

# Refresh flags that channel-rack changes report through (channel add/remove/select, group, name and
# colour changes). Channel volume/pan value changes arrive via OnDirtyChannel instead (see below); these
# flags cover the display-oriented changes and give an instant repaint when they fire.
CHANNEL_REFRESH_FLAGS = (
    midi.HW_ChannelEvent
    | midi.HW_Dirty_Tracks
    | midi.HW_Dirty_ControlValues
    | midi.HW_Dirty_FocusedWindow
    | midi.HW_Dirty_ChannelRackGroup
    | midi.HW_Dirty_Names
    | midi.HW_Dirty_Colors
)

class ChannelBankedTrackBaseBehavior(McuBaseBehavior):
    """
    Base behavior for banked channel-rack behaviors (e.g. ChannelFaderBehavior, ChannelMuteButtonBehavior).

    Parallel to MixerBankedTrackBaseBehavior, but a banked virtual index is a channel-rack channel rather
    than a mixer track. Subclasses implement Update().

    FL delivers channel value changes (volume/pan/mute/solo) through OnDirtyChannel (the channel-rack
    analog of OnDirtyMixerTrack), so this base repaints on that callback, on bank changes, and on the
    refresh flags above.
    """

    def __init__(self, mcuDevice: McuDevice, trackBankingManager: TrackBankingManager, refreshFlagsToCheck: int = CHANNEL_REFRESH_FLAGS):
        super().__init__(mcuDevice)
        self.__trackBanking = trackBankingManager
        self.__refreshFlagsToCheck = refreshFlagsToCheck

    def OnEnable(self):
        super().OnEnable()
        self.TrackBanking.AddTrackChangeSubscriber(self.OnTrackBankChange)
        # Paint immediately so the current state is reflected as soon as the behavior is enabled.
        self.Update()

    def OnDisable(self):
        self.TrackBanking.RemoveTrackChangeSubscriber(self.OnTrackBankChange)
        super().OnDisable()

    def OnTrackBankChange(self, newFirstTrack):
        """Repaint immediately when the bank changes (FL fires no refresh for controller-side banking)."""
        self.Update()

    def OnDirtyChannel(self, index):
        # FL marks a channel dirty here on any channel change (including volume/pan). Repaint the bank; the
        # HAL dedups unchanged state, so this stays cheap even when fired once per channel.
        self.Update()

    def OnRefresh(self, flags):
        super().OnRefresh(flags)
        if flags & self.__refreshFlagsToCheck:
            self.Update()

    def Update(self):
        """Called when the current behavior needs to be updated because something changed on the channel rack."""
        pass

    @property
    def TrackBanking(self):
        return self.__trackBanking
