import time

import device
import ui

from behaviors.mcu_base_behavior import McuBaseBehavior
from utilities.track_banking_manager import TrackBankingManager
from device_hal.mcu_device import McuDevice


class MixerShowBankInFLBehavior(McuBaseBehavior):
    """Behavior that shows a short overlay in the FL Studio mixer when the track bank changes."""

    def __init__(self, mcuDevice: McuDevice, trackBankingManager: TrackBankingManager):
        super().__init__(mcuDevice)
        self._trackBanking = trackBankingManager

    def OnEnable(self):
        super().OnEnable()
        if (not self.McuDevice.isExtender):
            self._trackBanking.AddTrackChangeSubscriber(self._onTrackBankChange)

    def OnDisable(self):
        if (not self.McuDevice.isExtender):
            self._trackBanking.RemoveTrackChangeSubscriber(self._onTrackBankChange)
        super().OnDisable()

    def _onTrackBankChange(self, _newFirstTrack: int):
        """Called when track banking changes; show an overlay in the mixer if available."""
        firstTrack = self._trackBanking.GetFirstTrack()
        ui.miDisplayRect(firstTrack, firstTrack + self._trackBanking.TrackCount * (1 + device.dispatchReceiverCount()), 1000)
