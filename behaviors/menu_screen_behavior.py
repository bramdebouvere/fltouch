import midi
import mixer

from behaviors.mcu_base_screen_behavior import McuBaseScreenBehavior
from constants import menu_items
from constants.mcu_constants import OffOnStr, ScribbleStripWidth
from device_hal.mcu_colors import GetMcuColor, ScreenColorBlack
from device_hal.mcu_device import McuDevice
from utilities.track_banking_manager import TrackBankingManager

class MenuScreenBehavior(McuBaseScreenBehavior):
    """
    Screen behavior for the Flip menu.

    For the menu items currently banked onto this unit it shows the item label (top row) and its
    current on/off state for the selected track (bottom row). A virtual index here is a menu item, 
    not a mixer track, so it targets mixer.trackNumber() (the active track) directly.
    """

    def __init__(self, mcuDevice: McuDevice, trackBankingManager: TrackBankingManager):
        super().__init__(mcuDevice, trackBankingManager)

    def OnEnable(self):
        super().OnEnable()
        self.RenderScreen()

    def OnRefresh(self, flags):
        super().OnRefresh(flags)

        # Re-render on selection change (retarget to another track) and when values change (menu item selection)
        if flags & (midi.HW_Dirty_Mixer_Sel | midi.HW_Dirty_Mixer_Controls):
            self.RenderScreen()

    def RenderScreen(self):
        """Render the labels and current values for the menu items currently banked on this unit."""
        track = mixer.trackNumber()

        topText = ''
        bottomText = ''
        colorArr = []

        for virtualIndex in self._trackBanking.GetTrackIndexes():
            if not self._trackBanking.VirtualTrackExists(virtualIndex):
                topText += ' ' * ScribbleStripWidth
                bottomText += ' ' * ScribbleStripWidth
                colorArr.append(GetMcuColor(ScreenColorBlack))
                continue

            topText += menu_items.GetMenuItemLabel(virtualIndex).center(ScribbleStripWidth)[:ScribbleStripWidth]
            value = menu_items.GetMenuItemValue(virtualIndex, track)
            # Plain actions have no on/off state (GetMenuItemValue returns None) -> leave the bottom row blank
            valueText = ' ' * ScribbleStripWidth if value is None else OffOnStr[int(value)]
            bottomText += valueText.center(ScribbleStripWidth)[:ScribbleStripWidth]
            colorArr.append(menu_items.GetMenuItemColor(virtualIndex))

        self.McuDevice.SetTextDisplay(topText, 0, skipIsAssignedCheck=True)
        self.McuDevice.SetTextDisplay(bottomText, 1, skipIsAssignedCheck=True)
        self.McuDevice.SetScreenColors(colorArr, skipIsAssignedCheck=True)
