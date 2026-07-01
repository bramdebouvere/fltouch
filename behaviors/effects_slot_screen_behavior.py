import device
import midi
import mixer
import plugins

from behaviors.mcu_base_screen_behavior import McuBaseScreenBehavior
from constants.mcu_constants import ScribbleStripWidth
from device_hal.mcu_colors import GetMcuColor, ScreenColorBlack
from device_hal.mcu_device import McuDevice
from utilities.track_banking_manager import TrackBankingManager
from utilities.transliteration import TransliterateToAscii

# FL colour int that GetMcuColor maps to a white scribble strip (used for slots with no plugin).
_WHITE = 0xFFFFFF

class EffectsSlotScreenBehavior(McuBaseScreenBehavior):
    """
    Screen behavior for the Effects slot overview.

    For the effect slots currently banked onto this unit it shows the slot number (top row) and the
    plugin name (bottom row), coloured with the plugin's own FL Studio colour. Empty slots show only
    the slot number on a black strip; slot indexes beyond the 10 available are left blank.

    Like the EQ screen, a virtual index here is an effect slot of the selected mixer track, not a mixer
    track, so it targets mixer.trackNumber() directly.
    """

    def __init__(self, mcuDevice: McuDevice, trackBankingManager: TrackBankingManager):
        super().__init__(mcuDevice, trackBankingManager)

    def OnEnable(self):
        super().OnEnable()
        self.RenderScreen()

    def OnRefresh(self, flags):
        super().OnRefresh(flags)

        # Re-render on selection change (retarget to another track) and when plugin values, colours or
        # names change.
        if flags & (midi.HW_Dirty_Mixer_Sel | midi.HW_Dirty_Mixer_Controls | midi.HW_Dirty_Colors | midi.HW_Dirty_Names):
            self.RenderScreen()

    def RenderScreen(self):
        """Render the slot numbers, plugin names and colours for the slots currently banked on this unit."""
        track = mixer.trackNumber()

        topText = ''
        bottomText = ''
        colorArr = []

        for virtualIndex in self._trackBanking.GetTrackIndexes():
            if not self._trackBanking.VirtualTrackExists(virtualIndex):
                # Index beyond the available effect slots -> fully blank
                topText += ' ' * ScribbleStripWidth
                bottomText += ' ' * ScribbleStripWidth
                colorArr.append(GetMcuColor(ScreenColorBlack))
                continue

            # Slot numbers are 1-based for display
            topText += str(virtualIndex + 1).center(ScribbleStripWidth)[:ScribbleStripWidth]

            if mixer.isTrackPluginValid(track, virtualIndex):
                name = TransliterateToAscii(plugins.getPluginName(track, virtualIndex, True)).strip()
                bottomText += name.center(ScribbleStripWidth)[:ScribbleStripWidth]
                # getSlotColor returns the FX slot's own colour. A slot can still report no colour (0),
                # which would map to black; fall back to white so a populated slot is never shown black.
                flColor = mixer.getSlotColor(track, virtualIndex)
                colorArr.append(_WHITE if GetMcuColor(flColor) == ScreenColorBlack else flColor)
            else:
                # Slot exists but is empty -> show "<empty>" on a white strip (black is reserved for slot
                # indexes beyond the 10 available).
                bottomText += '<empty>'.center(ScribbleStripWidth)[:ScribbleStripWidth]
                colorArr.append(_WHITE)

        if (device.isAssigned()):
            self.McuDevice.SetTextDisplay(topText, 0, skipIsAssignedCheck=True)
            self.McuDevice.SetTextDisplay(bottomText, 1, skipIsAssignedCheck=True)
            self.McuDevice.SetScreenColors(colorArr, skipIsAssignedCheck=True)
