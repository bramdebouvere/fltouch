import device
import midi
import transport
import ui

from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal import mcu_buttons


class PluginPickerButtonBehavior(McuBaseBehavior):
    """Opens the plugin picker when the Smooth button is pressed."""

    def OnMidiMsg(self, event):
        if event.midiId == midi.MIDI_NOTEON and event.data1 == mcu_buttons.Smooth:
            if event.data2 > 0 and event.pmeFlags & midi.PME_System_Safe:
                try:
                    ui.showPicker(0, 1) # type: ignore - ONLY SUPPORTED FROM API 41, not yet in public release
                except AttributeError:
                    transport.globalTransport(midi.FPT_F8, 2, event.pmeFlags)
            device.directFeedback(event)
            event.handled = True
            return event

        return super().OnMidiMsg(event)
