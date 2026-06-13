import device
import midi
import transport
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

            # Shift + any function button sends FPT_F1–FPT_F8
            if ButtonManager.ShiftPressed:
                transport.globalTransport(
                    midi.FPT_F1 + btn - mcu_buttons.Cut,
                    int(event.data2 > 0) * 2,
                    event.pmeFlags,
                )
                device.directFeedback(event)
                event.handled = True
                return event

            if btn == mcu_buttons.Undo:
                # Undo toggles as a jog source; jog wheel then navigates undo history
                if event.data2 == 0:
                    if ButtonManager.JogSource == btn:
                        ButtonManager.JogSource = 0
                else:
                    if ButtonManager.JogSource == 0:
                        ButtonManager.JogSource = btn

            elif btn in [mcu_buttons.Cut, mcu_buttons.Copy, mcu_buttons.Paste, mcu_buttons.Insert, mcu_buttons.Delete]:
                transport.globalTransport(
                    midi.FPT_Cut + btn - mcu_buttons.Cut,
                    int(event.data2 > 0) * 2,
                    event.pmeFlags,
                )

            elif btn == mcu_buttons.ItemMenu:
                if event.pmeFlags & midi.PME_System_Safe:
                    transport.globalTransport(midi.FPT_ItemMenu, int(event.data2 > 0) * 2, event.pmeFlags)

            elif btn == mcu_buttons.UndoRedo:
                if event.pmeFlags & midi.PME_System_Safe:
                    transport.globalTransport(midi.FPT_Undo, int(event.data2 > 0) * 2, event.pmeFlags)

            device.directFeedback(event)
            event.handled = True
            return event

        return super().OnMidiMsg(event)
