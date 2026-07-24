from behaviors.fader_touch_suppress_behavior import FaderTouchSuppressBehavior
from behaviors.flip_button_behavior import FlipButtonBehavior
from behaviors.menu_flip_led_behavior import MenuFlipLedBehavior
from behaviors.menu_screen_behavior import MenuScreenBehavior
from behaviors.menu_select_button_behavior import MenuSelectButtonBehavior
from behaviors.menu_select_led_behavior import MenuSelectLedBehavior
from behaviors.plugin_picker_button_behavior import PluginPickerButtonBehavior
from behaviors.track_banking_behavior import TrackBankingBehavior
from datatypes.menu_item import MenuItem
from device_hal.mcu_device import McuDevice
from modes.mcu_base_mode import McuBaseMode
from modes.mcu_composite_mode import McuCompositeMode
from utilities.track_banking_manager import TrackBankingManager

class McuMenuMode(McuBaseMode):
    """
    Flip menu sub-mode: a bank of utility functions, one per channel strip on the XTouch. SELECT
    runs the item's action. Pressing FLIP again returns to the previous sub-mode.
    """

    def __init__(self, device: McuDevice, menuBankingManager: TrackBankingManager, compositeMode: McuCompositeMode,
                 menuItems: list[MenuItem], closeKey: int, pickerCategory: int = 1):
        menuScreenBehavior = MenuScreenBehavior(device, menuBankingManager, menuItems)
        super().__init__(device, [
            menuScreenBehavior,
            TrackBankingBehavior(device, menuBankingManager),
            MenuSelectLedBehavior(device, menuBankingManager),
            MenuSelectButtonBehavior(device, menuBankingManager, menuScreenBehavior, menuItems),
            FlipButtonBehavior(device, compositeMode, closeKey),
            MenuFlipLedBehavior(device),
            FaderTouchSuppressBehavior(device),
            PluginPickerButtonBehavior(device, pickerCategory),
        ], menuBankingManager)
