import time

import mixer

from typing import Callable

from behaviors.mcu_base_behavior import McuBaseBehavior
from constants.mcu_constants import ScribbleStripWidth
from device_hal.mcu_colors import GetMcuColor, ScreenColorBlack
from utilities.track_banking_manager import TrackBankingManager
from utilities.transliteration import GetAsciiSafeTrackName
from device_hal.mcu_device import McuDevice

class McuBaseScreenBehavior(McuBaseBehavior):
    """Behavior for the screen."""

    def __init__(self, mcuDevice: McuDevice, trackBankingManager: TrackBankingManager):
        super().__init__(mcuDevice)
        self.__trackBanking = trackBankingManager
        self.__callbackTime: float | None = None
        self.__callback: Callable[[], None] | None = None

    def OnEnable(self):
        super().OnEnable()
        self.__trackBanking.AddTrackChangeSubscriber(self._onTrackBankChange)

    def OnDisable(self):
        self.__trackBanking.RemoveTrackChangeSubscriber(self._onTrackBankChange)

        # Clear screen & colors
        self.McuDevice.SetTextDisplay('', 1, skipIsAssignedCheck = True)
        self.McuDevice.SetScreenColors(skipIsAssignedCheck = True)

        super().OnDisable()

    def OnIdle(self):
        # Check if we have a callback to execute (for temporary messages)
        if (self.__callback is not None and self.__callbackTime is not None and time.time() >= self.__callbackTime):
            callback = self.__callback
            self.__callback = None
            self.__callbackTime = None
            callback()

        super().OnIdle()

    def _onTrackBankChange(self, newFirstTrack):
        pass

    def OnRefresh(self, flags):
        super().OnRefresh(flags)

    def RenderTrackNumbers(self, row: int):
        """Render track numbers on the screen based on the current track bank."""

        tracks = self.__trackBanking.GetTrackIndexes();
        text = ''
        for track in tracks:
            text += f'{track:^{ScribbleStripWidth}}' # center the track number within the space on the scribble strip screen
        self.McuDevice.SetTextDisplay(text, row, skipIsAssignedCheck=True)

    def RenderTrackNames(self, row: int):
        """Render track names on the screen based on the current track bank."""
        tracks = self.__trackBanking.GetTrackIndexes()
        text = ''
        for track in tracks:
            if self.__trackBanking.VirtualTrackExists(track):
                text += GetAsciiSafeTrackName(track, ScribbleStripWidth).ljust(ScribbleStripWidth)
            else:
                text += '<empty>'.center(ScribbleStripWidth)
        self.McuDevice.SetTextDisplay(text, row, skipIsAssignedCheck=True)

    def RenderTrackColors(self):
        """Render track colors on the screen based on the current track bank."""
        tracks = self.__trackBanking.GetTrackIndexes()
        colorArr = []
        for track in tracks:
            if self.__trackBanking.VirtualTrackExists(track):
                colorArr.append(mixer.getTrackColor(track))
            else:
                colorArr.append(GetMcuColor(ScreenColorBlack))
        self.McuDevice.SetScreenColors(colorArr, skipIsAssignedCheck=True)

    def RenderTrackWhite(self):
        """Set all screen sections to white (default)."""
        self.McuDevice.SetScreenColors();

    def RenderMessage(self, message: str, row: int, duration: int = 2000, callback: Callable[[int], None] | None = None):
        """
        Render a message on the screen. If a callback is provided, it will be called when the message expires.
        :param message: The message to display
        :param row: The row to display the message on (0 = top, 1 = bottom)
        :param duration: How long to display the message in milliseconds
        :param callback: An optional callback to call when the message expires. The callback will receive the row of the message as an argument.
        """
        # Clear any existing callback
        if self.__callback is not None:
            self.__callback = None

        # Display the message
        self.McuDevice.SetTextDisplay(message, row, skipIsAssignedCheck=True)

        # If a callback is provided, schedule it to be called when the message expires
        # (for example for removing the message from the screen again)
        # Using python Timers is not possible in FL Studio, so we will use the OnIdle method to check if enough time has passed
        if callback is not None:
            self.__callback = lambda: callback(row)
            self.__callbackTime = time.time() + duration / 1000
