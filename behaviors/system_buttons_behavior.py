import midi
import transport
from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal import mcu_buttons
from utilities.button_manager import ButtonManager


class SystemButtonsBehavior(McuBaseBehavior):
    """Handles system-level buttons: Save, Menu, Escape, Enter."""

    def __init__(self, mcuDevice):
        super().__init__(mcuDevice)

    def OnMidiMsg(self, event):
        if event.midiId != midi.MIDI_NOTEON:
            return super().OnMidiMsg(event)

        if event.data1 == mcu_buttons.Save:
            # Save project; Shift+Save = Save New
            transport.globalTransport(midi.FPT_Save + int(ButtonManager.ShiftPressed), int(event.data2 > 0) * 2, event.pmeFlags)
            event.handled = True
            return event

        elif event.data1 == mcu_buttons.Menu:
            # Opens a menu. This can be the FL Studio main menu, or a context menu in one of the windows
            transport.globalTransport(midi.FPT_Menu, int(event.data2 > 0) * 2, event.pmeFlags)
            event.handled = True
            return event

        elif event.data1 == mcu_buttons.Escape:
            # Escape / close dialog; Shift+Escape = answer No (FPT_No) to a dialog
            fpt = midi.FPT_No if ButtonManager.ShiftPressed else midi.FPT_Escape
            transport.globalTransport(fpt, int(event.data2 > 0) * 2, event.pmeFlags)
            event.handled = True
            return event

        elif event.data1 == mcu_buttons.Enter:
            # Confirm / accept; Shift+Enter = answer Yes (FPT_Yes) to a dialog
            fpt = midi.FPT_Yes if ButtonManager.ShiftPressed else midi.FPT_Enter
            transport.globalTransport(fpt, int(event.data2 > 0) * 2, event.pmeFlags)
            event.handled = True
            return event

        return super().OnMidiMsg(event)
