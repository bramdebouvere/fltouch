
from behaviors.mcu_mixer_screen_behavior import McuMixerScreenBehavior
from behaviors.mixer_fader_behavior import MixerFaderBehavior
from behaviors.mixer_meter_behavior import MixerMeterBehavior
from behaviors.mixer_mute_button_behavior import MixerMuteButtonBehavior
from behaviors.mixer_rec_button_behavior import MixerRecButtonBehavior
from behaviors.mixer_select_button_behavior import MixerSelectButtonBehavior
from behaviors.mixer_show_bank_in_fl_behavior import MixerShowBankInFLBehavior
from behaviors.mixer_solo_button_behavior import MixerSoloButtonBehavior
from behaviors.mixer_encoder_stereo_behavior import MixerEncoderStereoBehavior
from behaviors.track_banking_behavior import TrackBankingBehavior
from utilities.track_banking_manager import TrackBankingManager
from device_hal.mcu_device import McuDevice
from modes.mcu_base_mode import McuBaseMode
from utilities.fl_class_import import FlMidiMsg

class McuStereoMode(McuBaseMode):

    def __init__(self, device: McuDevice, trackBankingManager: TrackBankingManager):
        screenBehavior = McuMixerScreenBehavior(device, trackBankingManager)
        super().__init__(device, [
            screenBehavior,
            TrackBankingBehavior(device, trackBankingManager),
            MixerFaderBehavior(device, trackBankingManager),
            MixerMeterBehavior(device, trackBankingManager),
            MixerSelectButtonBehavior(device, trackBankingManager),
            MixerRecButtonBehavior(device, trackBankingManager, screenBehavior),
            MixerSoloButtonBehavior(device, trackBankingManager),
            MixerMuteButtonBehavior(device, trackBankingManager),
            MixerShowBankInFLBehavior(device, trackBankingManager),
            MixerEncoderStereoBehavior(device, trackBankingManager),
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