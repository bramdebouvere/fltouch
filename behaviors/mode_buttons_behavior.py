import device
import midi
from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal import mcu_buttons


class ModeButtonsBehavior(McuBaseBehavior):
    """Lights up the LED for the mode this behavior belongs to when enabled, and dims all others."""

    def __init__(self, mcuDevice, modeButton: int):
        super().__init__(mcuDevice)
        self._modeButton = modeButton

    def OnEnable(self):
        """Light up this mode's button and dim all others"""
        if device.isAssigned():
            # Calculate which index position this button is at (0-5)
            buttonIndex = self._modeButton - mcu_buttons.Pan
            
            for i in range(6):
                self.McuDevice.SetButton(
                    mcu_buttons.Pan + i,
                    midi.TranzPort_OffOnT[i == buttonIndex],
                    5 + i
                )
