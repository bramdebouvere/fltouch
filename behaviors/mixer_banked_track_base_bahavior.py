import midi

from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal.mcu_device import McuDevice
from utilities.track_banking_manager import TrackBankingManager


class MixerBankedTrackBaseBehavior(McuBaseBehavior):
    """
    Base behavior for banked track behaviors (e.g. MixerFaderBehavior, MixerEncoderPanBehavior)
    This base class handles marking tracks as dirty when the bank changes and dirty mixer control events, so that inheriting classes can just implement the Update method
    """

    def __init__(self, mcuDevice: McuDevice, trackBankingManager: TrackBankingManager, refreshFlagToCheck=midi.HW_Dirty_Mixer_Controls):
        """
        Initialize the base behavior for banked mixer track behaviors
        
        Args:
            mcuDevice: The MCU device instance.
            trackBankingManager: Manager for track banking functionality.
            refreshFlagToCheck: MIDI flag to check for refresh events (default: midi.HW_Dirty_Mixer_Controls).
        """
        super().__init__(mcuDevice)
        self.__trackBanking = trackBankingManager
        self.__needsChanges = False
        self.__refreshFlagToCheck = refreshFlagToCheck

    def OnEnable(self):
        super().OnEnable()
        self.TrackBanking.AddTrackChangeSubscriber(self.OnTrackBankChange)
        # Mark for changes so Update will run after enabling this behavior, so changes are reflected immediately
        self.__needsChanges = True
        self.OnRefresh(self.__refreshFlagToCheck)

    def OnDisable(self):
        self.TrackBanking.RemoveTrackChangeSubscriber(self.OnTrackBankChange)
        super().OnDisable()

    def OnTrackBankChange(self, newFirstTrack):
        """Called when track banking changes, mark all tracks dirty to refresh controls."""
        self.OnDirtyMixerTrack(-1)  # mark all tracks dirty to ensure controls are refreshed for new tracks in bank

    
    def OnDirtyMixerTrack(self, trackNum):
        """Track which mixer tracks are dirty so we can refresh encoders on the next HW refresh."""
        if trackNum == -1:
            self.__needsChanges = True
            return

        trackIndexes = self.TrackBanking.GetTrackIndexes()
        if trackNum not in trackIndexes:
            return

        self.__needsChanges = True

    def OnRefresh(self, flags):
        super().OnRefresh(flags)

        if not (flags & self.__refreshFlagToCheck):
            return

        if not self.__needsChanges:
            return
        
        self.Update()
        
        self.__needsChanges = False

    def Update(self):
        """Called when the current behavior needs to be updated because something changed in the mixer."""
        pass

    @property
    def TrackBanking(self):
        return self.__trackBanking
