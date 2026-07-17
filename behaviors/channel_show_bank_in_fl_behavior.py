import device
import ui
import midi

from behaviors.mcu_base_behavior import McuBaseBehavior
from utilities.track_banking_manager import TrackBankingManager
from device_hal.mcu_device import McuDevice

class ChannelShowBankInFLBehavior(McuBaseBehavior):
    """
    Behavior that flashes a rectangle over the channel rack channel list when the channel bank changes.
    """

    def __init__(self, mcuDevice: McuDevice, channelRackManager: TrackBankingManager):
        super().__init__(mcuDevice)
        self._trackBanking = channelRackManager

    def OnEnable(self):
        super().OnEnable()
        if (not self.McuDevice.isExtender):
            self._trackBanking.AddTrackChangeSubscriber(self._onTrackBankChange)

    def OnDisable(self):
        if (not self.McuDevice.isExtender):
            self._trackBanking.RemoveTrackChangeSubscriber(self._onTrackBankChange)
        super().OnDisable()

    def _onTrackBankChange(self, _newFirstChannel: int):
        """Called when channel banking changes; flash a highlight over the banked channels in the rack."""
        firstChannel = self._trackBanking.GetFirstTrack() # first track on any device
        count = self._trackBanking.TrackCount * (1 + device.dispatchReceiverCount())

        # Vertical axis (top/bottom) = channel rows; CR_HighlightChannels draws on the channel list,
        # CR_ScrollToView keeps the banked channels on-screen. left/right span the full grid width.
        ui.crDisplayRect(0, firstChannel, midi.MaxInt, firstChannel + count, 1000,
                         midi.CR_HighlightChannels | midi.CR_ScrollToView)
