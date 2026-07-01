from behaviors.effects_slot_screen_behavior import EffectsSlotScreenBehavior
from behaviors.effects_slot_encoder_behavior import EffectsSlotEncoderBehavior
from behaviors.effects_slot_mute_button_behavior import EffectsSlotMuteButtonBehavior
from behaviors.effects_slot_select_button_behavior import EffectsSlotSelectButtonBehavior
from behaviors.track_banking_behavior import TrackBankingBehavior
from device_hal.mcu_device import McuDevice
from modes.mcu_base_mode import McuBaseMode
from utilities.track_banking_manager import TrackBankingManager

class McuEffectSlotsMode(McuBaseMode):
    """
    Effects mode Slot overview sub-mode.

    Spreads the selected mixer track's 10 effect slots across the strips (banked through the slot
    banking manager). Encoder = slot mix level, MUTE button = bypass, screen = slot number + plugin
    name in the plugin's colour, SELECT = open the plugin and switch to the parameter sub-mode.
    """

    def __init__(self, device: McuDevice, slotBankingManager: TrackBankingManager, compositeMode):
        super().__init__(device, [
            EffectsSlotScreenBehavior(device, slotBankingManager),
            EffectsSlotEncoderBehavior(device, slotBankingManager),
            EffectsSlotMuteButtonBehavior(device, slotBankingManager),
            TrackBankingBehavior(device, slotBankingManager),
            EffectsSlotSelectButtonBehavior(device, slotBankingManager, compositeMode),
        ], slotBankingManager)
