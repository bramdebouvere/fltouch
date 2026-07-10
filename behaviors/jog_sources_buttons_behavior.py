import device
import midi
from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal import mcu_buttons
from utilities.button_manager import ButtonManager

class JogSourcesButtonsBehavior(McuBaseBehavior):
    """Handles the row of jog source buttons (Pattern, Mixer, Channels, Tempo, Free1-4)."""

    def __init__(self, mcuDevice):
        super().__init__(mcuDevice)

    def OnMidiMsg(self, event):
        if event.midiId == midi.MIDI_NOTEON and event.data1 in [
            mcu_buttons.Pattern,
            mcu_buttons.Mixer,
            mcu_buttons.Channels,
            mcu_buttons.Tempo,
            mcu_buttons.Free1,
            mcu_buttons.Free2,
            mcu_buttons.Free3,
            mcu_buttons.Free4,
        ]:
            btn = event.data1
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
