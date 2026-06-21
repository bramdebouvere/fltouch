import midi
import mixer

from behaviors.mcu_base_screen_behavior import McuBaseScreenBehavior
from constants.mcu_constants import ScribbleStripWidth
from constants import eq_controls
from device_hal.mcu_colors import GetMcuColor, ScreenColorBlack
from device_hal.mcu_device import McuDevice
from utilities.track_banking_manager import TrackBankingManager
from utilities.transliteration import TransliterateToAscii


class EqScreenBehavior(McuBaseScreenBehavior):
    """
    Screen behavior for EQ mode.

    For the EQ controls currently banked onto this unit's encoders it shows the control label (top row),
    the live value (bottom row) and a per-shelf color (low = red, peaking = green, high = blue).
    Encoders with no assigned control are left blank/black. Temporary hint messages (OnSendTempMsg)
    flash on the top row and then restore, mirroring the mixer screen behavior.
    """

    def __init__(self, mcuDevice: McuDevice, trackBankingManager: TrackBankingManager):
        self.__messageToRender: str | None = None
        self.__messageDuration: int = 0
        super().__init__(mcuDevice, trackBankingManager)

    def OnEnable(self):
        super().OnEnable()
        self.RenderScreen()

    def OnDisable(self):
        # Base clears row 1 and the colors; also clear the top row
        self.McuDevice.SetTextDisplay('', 0, skipIsAssignedCheck=True)
        super().OnDisable()

    def _onTrackBankChange(self, newFirstTrack):
        self.RenderScreen()

    def OnRefresh(self, flags):
        super().OnRefresh(flags)

        # Re-render on selection change (retarget) and on control changes (values move as encoders turn)
        if flags & (midi.HW_Dirty_Mixer_Sel | midi.HW_Dirty_Mixer_Controls):
            self.RenderScreen()

    def OnSendTempMsg(self, msg: str, duration=2000):
        # We want to render this message immediately, but an OnRefresh might come directly after this, which would overwrite the screen
        # So we will render the message in the OnIdle method, which will come after any OnRefresh calls.
        self.__messageToRender = msg
        self.__messageDuration = duration
        return super().OnSendTempMsg(msg, duration)

    def OnIdle(self):
        if self.__messageToRender is not None:
            super().RenderMessage(self.__messageToRender, row=0, duration=self.__messageDuration, callback=lambda row: self.RenderScreen())
            self.__messageToRender = None
            self.__messageDuration = 0

        super().OnIdle()

    def RenderScreen(self):
        """Render the EQ labels, live values and colors for the controls currently banked on this unit."""
        baseEventId = mixer.getTrackPluginId(mixer.trackNumber(), 0)

        topText = ''
        bottomText = ''
        colorArr = []

        for virtualIndex in self._trackBanking.GetTrackIndexes():
            if self._trackBanking.VirtualTrackExists(virtualIndex):
                topText += eq_controls.label_of(virtualIndex).center(ScribbleStripWidth)[:ScribbleStripWidth]

                eventId = eq_controls.event_id_of(baseEventId, virtualIndex)
                rawValue = mixer.getAutoSmoothEventValue(eventId)
                valueStr = TransliterateToAscii(mixer.getEventIDValueString(eventId, rawValue)).strip()
                bottomText += valueStr.center(ScribbleStripWidth)[:ScribbleStripWidth]

                colorArr.append(eq_controls.color_of(virtualIndex))
            else:
                topText += ' ' * ScribbleStripWidth
                bottomText += ' ' * ScribbleStripWidth
                colorArr.append(GetMcuColor(ScreenColorBlack))

        self.McuDevice.SetTextDisplay(topText, 0, skipIsAssignedCheck=True)
        self.McuDevice.SetTextDisplay(bottomText, 1, skipIsAssignedCheck=True)
        self.McuDevice.SetScreenColors(colorArr, skipIsAssignedCheck=True)
