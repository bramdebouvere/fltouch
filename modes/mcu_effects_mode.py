
from behaviors.track_banking_behavior import TrackBankingBehavior
from utilities.track_banking_manager import TrackBankingManager
from device_hal.mcu_device import McuDevice
from modes.mcu_base_mode import McuBaseMode
from utilities.fl_class_import import FlMidiMsg


class McuEffectsMode(McuBaseMode):

    def __init__(self, device: McuDevice, trackBankingManager: TrackBankingManager):
        super().__init__(device, [
            TrackBankingBehavior(device, trackBankingManager)
        ], trackBankingManager)

    def OnEnable(self):
        super().OnEnable()

    def OnDisable(self):
        super().OnDisable()

    def OnDirtyMixerTrack(self, SetTrackNum):
        super().OnDirtyMixerTrack(SetTrackNum)

    def OnUpdateMeters(self):
        super().OnUpdateMeters()

    def OnIdle(self):
        super().OnIdle()

    def OnSendTempMsg(self, msg: str, duration = 1000):
        super().OnSendTempMsg(msg, duration)

    def OnRefresh(self, flags):
        super().OnRefresh(flags)

    def OnMidiMsg(self, event: FlMidiMsg):
        super().OnMidiMsg(event)

    def OnSysEx(self, event: FlMidiMsg):
        super().OnSysEx(event)

    def OnFirstConnect(self):
        super().OnFirstConnect()

    def OnProjectLoad(self, status: int):
        super().OnProjectLoad(status)

    def OnUpdateBeatIndicator(self, value: int):
        super().OnUpdateBeatIndicator(value)

    def OnWaitingForInput(self):
        super().OnWaitingForInput()