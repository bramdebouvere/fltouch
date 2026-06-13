import device
import midi
import transport
import ui
from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal import mcu_buttons
from utilities.button_manager import ButtonManager


class ArrowZoomButtonsBehavior(McuBaseBehavior):
    """Handles arrow buttons and zoom button."""

    def __init__(self, mcuDevice):
        super().__init__(mcuDevice)

    def OnMidiMsg(self, event):
        if event.midiId == midi.MIDI_NOTEON and event.data1 in [mcu_buttons.Up, mcu_buttons.Down, mcu_buttons.Left, mcu_buttons.Right]:
            # If no jog source button is pressed, the arrows should act as normal arrow buttons.
            if ButtonManager.JogSource == 0:
                transport.globalTransport(midi.FPT_Up - mcu_buttons.Up + event.data1, int(event.data2 > 0) * 2, event.pmeFlags)
            # If Zoom is the jog source (=zoom is pressed), the arrows should act as zoom buttons.
            elif ButtonManager.JogSource == mcu_buttons.Zoom:
                if event.data2 > 0:
                    isVertical = event.data1 in [mcu_buttons.Up, mcu_buttons.Down]
                    isPositive = event.data1 in [mcu_buttons.Up, mcu_buttons.Right]
                    step = 1 if isPositive else -1
                    transport.globalTransport(midi.FPT_HZoomJog + int(isVertical), step, event.pmeFlags)
            device.directFeedback(event)
            event.handled = True
            return event

        if event.midiId == midi.MIDI_NOTEON and event.data1 == mcu_buttons.Zoom:
            if ui.getFocused(midi.widBrowser):
                ui.selectBrowserMenuItem()

            # Zoom can act as a jog source
            if event.data2 == 0:
                if ButtonManager.JogSource == event.data1:
                    ButtonManager.JogSource = 0
            else:
                if ButtonManager.JogSource == 0:
                    ButtonManager.JogSource = event.data1

            device.directFeedback(event)
            event.handled = True
            return event

        return super().OnMidiMsg(event)
