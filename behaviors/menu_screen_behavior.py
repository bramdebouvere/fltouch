import midi

from behaviors.mcu_base_screen_behavior import McuBaseScreenBehavior
from datatypes.menu_item import MenuItem
from constants.mcu_constants import ScribbleStripWidth
from device_hal.mcu_colors import GetMcuColor, ScreenColorBlack
from device_hal.mcu_device import McuDevice
from utilities.track_banking_manager import TrackBankingManager

class MenuScreenBehavior(McuBaseScreenBehavior):
    """
    Screen behavior for the Flip menu.

    For the menu items currently banked onto this unit it shows the item label (top row) and its
    current on/off state (bottom row). A virtual index here is a menu item, not a mixer track.
    """

    def __init__(self, mcuDevice: McuDevice, trackBankingManager: TrackBankingManager, menuItems: list[MenuItem]):
        super().__init__(mcuDevice, trackBankingManager)
        self._menuItems = menuItems

    def OnEnable(self):
        super().OnEnable()
        self.RenderScreen()

    def OnRefresh(self, flags):
        super().OnRefresh(flags)

        # Re-render on selection change (retarget to another track) and when values change (menu item selection).
        # Skipped while a temporary message (e.g. "No free mixer track available") is on screen; the base
        # class restores the normal screen via RenderScreen once it expires.
        if flags & (midi.HW_Dirty_Mixer_Sel | midi.HW_Dirty_Mixer_Controls) and not self._isShowingTempMessage:
            self.RenderScreen()

    def RenderScreen(self):
        """Render the labels and current values for the menu items currently banked on this unit."""
        topText = ''
        bottomText = ''
        colorArr = []

        for virtualIndex in self._trackBanking.GetTrackIndexes():
            if not self._trackBanking.VirtualTrackExists(virtualIndex):
                topText += ' ' * ScribbleStripWidth
                bottomText += ' ' * ScribbleStripWidth
                colorArr.append(GetMcuColor(ScreenColorBlack))
                continue

            menuItem = self._menuItems[virtualIndex]
            topText += menuItem.label.center(ScribbleStripWidth)[:ScribbleStripWidth]
            menuItemValue = None if menuItem.getValue is None else menuItem.getValue()
            # Items with no getValue (plain actions, presets) -> leave the bottom row blank
            valueText = ' ' * ScribbleStripWidth if menuItemValue is None else menuItemValue
            bottomText += valueText.center(ScribbleStripWidth)[:ScribbleStripWidth]
            colorArr.append(menuItem.color)

        self.McuDevice.SetTextDisplay(topText, 0, skipIsAssignedCheck=True)
        self.McuDevice.SetTextDisplay(bottomText, 1, skipIsAssignedCheck=True)
        self.McuDevice.SetScreenColors(colorArr, skipIsAssignedCheck=True)
