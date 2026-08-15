import midi

from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal import mcu_buttons
from device_hal.mcu_device import McuDevice
from modes.mcu_composite_mode import McuCompositeMode
from utilities.fl_class_import import FlMidiMsg

class FlipButtonBehavior(McuBaseBehavior):
    """
    Flip: switches the composite mode to the sub-mode identified by targetSubModeKey.

    Used both to open a menu overlay (from an overview/parameter sub-mode) and to close it again
    (from within the menu sub-mode). targetSubModeKey is the sub-mode to switch to when the Flip button is pressed.
    """

    def __init__(self, mcuDevice: McuDevice, compositeMode: McuCompositeMode, targetSubModeKey: int):
        super().__init__(mcuDevice)
        self._compositeMode = compositeMode
        self._targetSubModeKey = targetSubModeKey

    def OnMidiMsg(self, event: FlMidiMsg) -> FlMidiMsg:
        if event.midiId == midi.MIDI_NOTEON and event.data1 == mcu_buttons.Flip and event.data2 > 0:
            self._compositeMode.SwitchTo(self._targetSubModeKey)
            event.handled = True
            return event
        return super().OnMidiMsg(event)
