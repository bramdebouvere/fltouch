import device
import midi
from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal import mcu_buttons


class SystemButtonsBehavior(McuBaseBehavior):
    """Handles system-level buttons: Save, Menu, Escape, Enter."""

    def __init__(self, mcuDevice):
        super().__init__(mcuDevice)

    def OnMidiMsg(self, event):
        if event.midiId == midi.MIDI_NOTEON and event.data1 in [
            mcu_buttons.Save,
            mcu_buttons.Menu,
            mcu_buttons.Escape,
            mcu_buttons.Enter,
        ]:
            device.directFeedback(event)
            event.handled = True
            return event

        return super().OnMidiMsg(event)
