import device
import midi
import channels

from behaviors.mcu_base_screen_behavior import McuBaseScreenBehavior
from constants.mcu_constants import ScribbleStripWidth
from device_hal.mcu_colors import GetMcuColor, ScreenColorBlack
from device_hal.mcu_device import McuDevice
from utilities.track_banking_manager import TrackBankingManager
from utilities.transliteration import GetAsciiSafeChannelName

class ChannelScreenBehavior(McuBaseScreenBehavior):
    """
    Screen behavior for the Channel Rack overview.

    For the channels currently banked onto this unit it shows the channel number (top row) and the
    channel name (bottom row), coloured with the channel's own FL Studio colour. Strips beyond the
    number of channels in the project are left blank.

    A virtual index here is a channel-rack channel (global index), not a mixer track.
    """

    def __init__(self, mcuDevice: McuDevice, trackBankingManager: TrackBankingManager):
        super().__init__(mcuDevice, trackBankingManager)

    def OnEnable(self):
        super().OnEnable()
        self.RenderScreen()

    def OnRefresh(self, flags):
        super().OnRefresh(flags)

        # Re-render when channels change (added/removed/renamed/recoloured) or the group/selection changes.
        if flags & (midi.HW_ChannelEvent | midi.HW_Dirty_FocusedWindow | midi.HW_Dirty_ChannelRackGroup |
                    midi.HW_Dirty_Colors | midi.HW_Dirty_Names):
            self.RenderScreen()

    def OnDirtyChannel(self, index):
        # Channel-rack property changes (colour, name, etc.) arrive here rather than through the mixer
        # refresh flags above, so repaint on this callback too - this is what reflects a colour change
        # (whether made from the controller via Shift+Name or directly in FL) onto the scribble strips.
        self.RenderScreen()

    def RenderScreen(self):
        """Render the channel numbers, names and colours for the channels currently banked on this unit."""
        topText = ''
        bottomText = ''
        colorArr = []

        for virtualIndex in self._trackBanking.GetTrackIndexes():
            if self._trackBanking.VirtualTrackExists(virtualIndex):
                # Channel numbers are 1-based for display
                topText += str(virtualIndex + 1).center(ScribbleStripWidth)[:ScribbleStripWidth]
                name = GetAsciiSafeChannelName(virtualIndex, ScribbleStripWidth).strip()
                bottomText += name.center(ScribbleStripWidth)[:ScribbleStripWidth]
                colorArr.append(channels.getChannelColor(virtualIndex, True))
            else:
                # Index beyond the available channels -> fully blank
                topText += ' ' * ScribbleStripWidth
                bottomText += ' ' * ScribbleStripWidth
                colorArr.append(GetMcuColor(ScreenColorBlack))

        if (device.isAssigned()):
            self.McuDevice.SetTextDisplay(topText, 0, skipIsAssignedCheck=True)
            self.McuDevice.SetTextDisplay(bottomText, 1, skipIsAssignedCheck=True)
            self.McuDevice.SetScreenColors(colorArr, skipIsAssignedCheck=True)
