import device
import midi
from behaviors.mcu_base_behavior import McuBaseBehavior
from constants.mcu_modes import ModeAssignmentLabels
from device_hal import mcu_buttons

class ModeButtonsBehavior(McuBaseBehavior):
    """Lights up the LED for the mode this behavior belongs to when enabled (dimming all others),
    and shows the mode's 2-char label on the assignment display."""

    def __init__(self, mcuDevice, modeButton: int):
        super().__init__(mcuDevice)
        self._modeButton = modeButton

    def OnEnable(self):
        # Mode buttons and the assignment display are both main-unit-only hardware.
        if self.McuDevice.isExtender or not device.isAssigned():
            return

        # Calculate which index position this button is at (0-5)
        buttonIndex = self._modeButton - mcu_buttons.Pan

        for i in range(6):
            self.McuDevice.SetButton(
                mcu_buttons.Pan + i,
                midi.TranzPort_OffOnT[i == buttonIndex],
                5 + i
            )

        self.McuDevice.SetAssignmentText(ModeAssignmentLabels.get(self._modeButton, '  '))
