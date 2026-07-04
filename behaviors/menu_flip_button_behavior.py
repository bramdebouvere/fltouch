import midi

from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal import mcu_buttons
from device_hal.mcu_device import McuDevice
from modes.mcu_composite_mode import McuCompositeMode
from utilities import mixer_menu_state
from utilities.fl_class_import import FlMidiMsg

class MenuFlipButtonBehavior(McuBaseBehavior):
    """Pressing Flip again while the menu is showing cancels back to the overview sub-mode."""

    def __init__(self, mcuDevice: McuDevice, compositeMode: McuCompositeMode):
        super().__init__(mcuDevice)
        self._compositeMode = compositeMode

    def OnMidiMsg(self, event: FlMidiMsg):
        if event.midiId == midi.MIDI_NOTEON and event.data1 == mcu_buttons.Flip and event.data2 > 0:
            self._compositeMode.SwitchTo(mixer_menu_state.OVERVIEW)
            event.handled = True
            return event
        return super().OnMidiMsg(event)
