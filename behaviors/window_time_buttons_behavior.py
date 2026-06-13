import device
import midi
from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal import mcu_buttons
from utilities.button_manager import ButtonManager


class WindowTimeButtonsBehavior(McuBaseBehavior):
    """Handles Browser, StepSequencer, Window, In, Out, Select buttons."""

    def __init__(self, mcuDevice):
        super().__init__(mcuDevice)

    def OnMidiMsg(self, event):
        if event.midiId == midi.MIDI_NOTEON and event.data1 in [
            mcu_buttons.Browser,
            mcu_buttons.StepSequencer,
            mcu_buttons.Window,
            mcu_buttons.In,
            mcu_buttons.Out,
            mcu_buttons.Select,
        ]:
            btn = event.data1
            # Window can act as a jog source
            if btn == mcu_buttons.Window:
                if event.data2 == 0:
                    if ButtonManager.JogSource == btn:
                        ButtonManager.JogSource = 0
                else:
                    if ButtonManager.JogSource == 0:
                        ButtonManager.JogSource = btn

            device.directFeedback(event)
            event.handled = True
            return event

        return super().OnMidiMsg(event)
