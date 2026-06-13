import device
import midi
from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal import mcu_buttons
from utilities.button_manager import ButtonManager


class FunctionButtonsBehavior(McuBaseBehavior):
    """Handles the F1-F8 function row (Cut, Copy, Paste, Insert, Delete, ItemMenu, Undo, Un/Redo)."""

    def __init__(self, mcuDevice):
        super().__init__(mcuDevice)

    def OnMidiMsg(self, event):
        if event.midiId == midi.MIDI_NOTEON and event.data1 in [
            mcu_buttons.Cut,
            mcu_buttons.Copy,
            mcu_buttons.Paste,
            mcu_buttons.Insert,
            mcu_buttons.Delete,
            mcu_buttons.ItemMenu,
            mcu_buttons.Undo,
            mcu_buttons.UndoRedo,
        ]:
            btn = event.data1
            # Undo can act as a jog source
            if btn == mcu_buttons.Undo:
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
