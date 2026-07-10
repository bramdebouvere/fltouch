import device
import midi
import transport
import ui
import general

from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal import mcu_buttons
from device_hal.mcu_device import McuDevice

class PluginPickerButtonBehavior(McuBaseBehavior):
    """
    Opens the plugin picker when the Smooth button is pressed.

    Category:
    - 0 (Plugin picker generators / Project picker patterns)
    - 1 (Plugin picker effects / Project picker channels) 
    """

    def __init__(self, device: McuDevice, category: int | None = None):
        super().__init__(device)
        self._category = category

    def OnMidiMsg(self, event):
        if event.midiId == midi.MIDI_NOTEON and event.data1 == mcu_buttons.Smooth:
            if event.data2 > 0 and event.pmeFlags & midi.PME_System_Safe:
                cat = self._category if self._category is not None else 1
                if (cat == 1):
                    ui.showWindow(midi.widMixer)
                    ui.setFocused(midi.widMixer)
                if (general.getVersion() >= 41):
                    ui.showPicker(0, cat) # type: ignore - ONLY SUPPORTED FROM API 41, only available in FL 2026
                else: # in case of older versions
                    transport.globalTransport(midi.FPT_F8, 2, event.pmeFlags)
            device.directFeedback(event)
            event.handled = True
            return event

        return super().OnMidiMsg(event)
