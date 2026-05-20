import midi
import mixer

from behaviors.mcu_base_behavior import McuBaseBehavior
from utilities.track_banking_manager import TrackBankingManager
from device_hal.mcu_device import McuDevice

class MixerMeterBehavior(McuBaseBehavior):
    """ This behavior is responsible for updating the peak meters on the MCU to reflect the peak values of the mixer tracks in FL Studio. """

    def __init__(self, mcuDevice: McuDevice, trackBankingManager: TrackBankingManager):
        super().__init__(mcuDevice)
        self.trackBanking = trackBankingManager

    def OnEnable(self):
        super().OnEnable()
        self.McuDevice.EnableMeters()

    def OnDisable(self):
        super().OnDisable()
        self.McuDevice.ClearMeters()
        self.McuDevice.DisableMeters()

    def OnUpdateMeters(self):
        """ Called when the peak meters have updated values in FL Studio and the hardware meters should be updated to reflect this change """
        super().OnUpdateMeters()
        trackIndexes = self.trackBanking.GetTrackIndexes()
        for index in trackIndexes:
            currentPeak = 0
            # Only show a value for meters for tracks that exist in FL Studio, otherwise the meter should be empty (0)
            if self.trackBanking.VirtualTrackExists(index):
                # Get track peak (what's displayed on the meter) from FL Studio
                currentPeak = mixer.getTrackPeaks(index, midi.PEAK_LR_INV)
            track = self.trackBanking.GetHardwareTrack(index)
            
            assert track is not None and track.meter is not None
            track.meter.SetValue(currentPeak)
