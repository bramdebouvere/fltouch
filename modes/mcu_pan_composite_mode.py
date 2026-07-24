from behaviors.mode_buttons_behavior import ModeButtonsBehavior
from constants import mixer_menu_items
from device_hal import mcu_buttons
from device_hal.mcu_device import McuDevice
from modes.mcu_composite_mode import McuCompositeMode
from modes.mcu_menu_mode import McuMenuMode
from modes.mcu_pan_mode import McuPanMode
from utilities import mixer_menu_state
from utilities.track_banking_manager import TrackBankingManager

class McuPanCompositeMode(McuCompositeMode):
    """
    Pan mode: the regular pan/mixer overview, plus the Flip menu as a second sub-mode.
    """

    def __init__(self, device: McuDevice, trackBankingManager: TrackBankingManager):
        super().__init__(device, [ModeButtonsBehavior(device, mcu_buttons.Pan)])

        overviewMode = McuPanMode(device, trackBankingManager, self)
        
        menuItems = mixer_menu_items.BuildMixerMenuItems()
        menuBankingManager = TrackBankingManager(device, len(menuItems))
        menuMode = McuMenuMode(device, menuBankingManager, self, menuItems, mixer_menu_state.OVERVIEW)

        self._addSubMode(mixer_menu_state.OVERVIEW, overviewMode)
        self._addSubMode(mixer_menu_state.MENU, menuMode)
