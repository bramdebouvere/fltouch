import device
import midi
import transport

from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal import mcu_buttons
from device_hal.mcu_device import McuDevice
from utilities.button_manager import ButtonManager


class MasterTransportSectionButtonsBehavior(McuBaseBehavior):
    """Behavior for master transport section buttons such as shift."""

    def __init__(self, mcuDevice: McuDevice):
        super().__init__(mcuDevice)

    def OnMidiMsg(self, event):
        if event.midiId == midi.MIDI_NOTEON and event.data1 == mcu_buttons.Shift:
            ButtonManager.ShiftPressed = event.data2 > 0
            device.directFeedback(event)
            event.handled = True
            return event

        return super().OnMidiMsg(event)
