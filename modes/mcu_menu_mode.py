from behaviors.menu_flip_button_behavior import MenuFlipButtonBehavior
from behaviors.menu_flip_led_behavior import MenuFlipLedBehavior
from behaviors.menu_screen_behavior import MenuScreenBehavior
from behaviors.menu_select_button_behavior import MenuSelectButtonBehavior
from behaviors.menu_select_led_behavior import MenuSelectLedBehavior
from behaviors.track_banking_behavior import TrackBankingBehavior
from device_hal.mcu_device import McuDevice
from modes.mcu_base_mode import McuBaseMode
from modes.mcu_composite_mode import McuCompositeMode
from utilities.track_banking_manager import TrackBankingManager

class McuMenuMode(McuBaseMode):
    """
    Flip menu sub-mode: a bank of track utility functions (see constants/menu_items.py), one per
    channel strip on the XTouch. SELECT runs the item's action against the selected track and returns to the
    overview sub-mode; Flip cancels back to the overview sub-mode without running anything.
    """

    def __init__(self, device: McuDevice, menuBankingManager: TrackBankingManager, compositeMode: McuCompositeMode):
        super().__init__(device, [
            MenuScreenBehavior(device, menuBankingManager),
            TrackBankingBehavior(device, menuBankingManager),
            MenuSelectLedBehavior(device, menuBankingManager),
            MenuSelectButtonBehavior(device, menuBankingManager, compositeMode),
            MenuFlipButtonBehavior(device, compositeMode),
            MenuFlipLedBehavior(device),
        ], menuBankingManager)
