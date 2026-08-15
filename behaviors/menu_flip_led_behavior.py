import midi

from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal import mcu_buttons
from device_hal.mcu_device import McuDevice

class MenuFlipLedBehavior(McuBaseBehavior):
    """Lights the Flip button's LED while the Flip menu sub-mode is active, off otherwise."""

    def __init__(self, mcuDevice: McuDevice):
        super().__init__(mcuDevice)

    def OnEnable(self):
        super().OnEnable()
        self.McuDevice.SetButton(mcu_buttons.Flip, midi.TranzPort_OffOnT[1], 18)

    def OnDisable(self):
        self.McuDevice.SetButton(mcu_buttons.Flip, midi.TranzPort_OffOnT[0], 18)
        super().OnDisable()
