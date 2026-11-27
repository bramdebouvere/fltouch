import midi
import mixer

from behaviors.effects_slot_screen_behavior import EffectsSlotScreenBehavior
from behaviors.effects_slot_encoder_behavior import EffectsSlotEncoderBehavior
from behaviors.effects_slot_mute_button_behavior import EffectsSlotMuteButtonBehavior
from behaviors.effects_slot_select_button_behavior import EffectsSlotSelectButtonBehavior
from behaviors.effects_slot_select_led_behavior import EffectsSlotSelectLedBehavior
from behaviors.namevalue_button_behavior import NameValueButtonBehavior
from behaviors.plugin_picker_button_behavior import PluginPickerButtonBehavior
from behaviors.track_banking_behavior import TrackBankingBehavior
from device_hal.mcu_device import McuDevice
from modes.mcu_base_mode import McuBaseMode
from utilities.effects_slot_count import GetEffectsSlotCount
from utilities.track_banking_manager import TrackBankingManager

class McuEffectSlotsMode(McuBaseMode):
    """
    Effects mode Slot overview sub-mode.

    Spreads the selected mixer track's effect slots across the strips (banked through the slot
    banking manager). Encoder = slot mix level, MUTE button = bypass, screen = slot number + plugin
    name in the plugin's colour, SELECT = open the plugin and switch to the parameter sub-mode.
    """

    def __init__(self, device: McuDevice, slotBankingManager: TrackBankingManager, compositeMode):
        screenBehavior = EffectsSlotScreenBehavior(device, slotBankingManager)
        super().__init__(device, [
            screenBehavior,
            EffectsSlotEncoderBehavior(device, slotBankingManager),
            EffectsSlotMuteButtonBehavior(device, slotBankingManager),
            TrackBankingBehavior(device, slotBankingManager),
            EffectsSlotSelectLedBehavior(device, slotBankingManager),
            EffectsSlotSelectButtonBehavior(device, slotBankingManager, compositeMode),
            NameValueButtonBehavior(device, slotBankingManager, screenBehavior),
            PluginPickerButtonBehavior(device),
        ], slotBankingManager)

    def OnEnable(self):
        self._UpdateSlotCount()
        super().OnEnable()

    def OnRefresh(self, flags):
        if not self._enabled:
            return

        # Keep in sync with dynamic slot count (since 26.2.0) when the selected track changes or its slot count changes
        if flags & (midi.HW_Dirty_Mixer_Sel | midi.HW_Dirty_Mixer_Controls):
            self._UpdateSlotCount()

        super().OnRefresh(flags)

    def _UpdateSlotCount(self):
        """Set the track banking manager's track count to the amount of FX slots on the current track."""
        assert self._trackBankingManager is not None
        self._trackBankingManager.softwareTrackCount = GetEffectsSlotCount(mixer.trackNumber())
