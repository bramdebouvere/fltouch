import midi

from behaviors.mcu_base_screen_behavior import McuBaseScreenBehavior
from utilities.track_banking_manager import TrackBankingManager
from device_hal.mcu_device import McuDevice


class McuMixerScreenBehavior(McuBaseScreenBehavior):
    """Behavior for the screen."""

    def __init__(self, mcuDevice: McuDevice, trackBankingManager: TrackBankingManager):
        self.__messageToRender: str | None = None
        self.__messageDuration: int = 0
        super().__init__(mcuDevice, trackBankingManager)

    def OnEnable(self):
        super().OnEnable()

    def OnDisable(self):
        super().OnDisable()

    def OnIdle(self):
        if (self.__messageToRender is not None):
            super().RenderMessage(self.__messageToRender, row=0, duration=self.__messageDuration, callback=lambda row: self.RenderScreen())
            super().RenderTrackNames(row=1)
            super().RenderTrackColors()
            self.__messageToRender = None
            self.__messageDuration = 0

        super().OnIdle()

    def OnSendTempMsg(self, msg: str, duration=2000):
        # We want to render this message immediately, but an OnRefresh might come directly after this, which would overwrite the screen
        # So we will render the message in the OnIdle method, which will come after any OnRefresh calls.
        self.__messageToRender = msg
        self.__messageDuration = duration
        return super().OnSendTempMsg(msg, duration)

    def OnRefresh(self, flags):
        super().OnRefresh(flags)
        
        # Update screen when mixer display changes
        if flags & midi.HW_Dirty_Mixer_Display:
            self.RenderScreen()

    def RenderScreen(self):
        """Update the screen content based on the current state of the mixer."""

        super().RenderTrackNumbers(row=0)
        super().RenderTrackNames(row=1)
        super().RenderTrackColors()
        pass
