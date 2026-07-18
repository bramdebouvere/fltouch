import midi

from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal import mcu_buttons
from device_hal.mcu_device import McuDevice
from utilities.fl_class_import import FlMidiMsg

class FaderTouchSuppressBehavior(McuBaseBehavior):
    """Swallows the fader *touch* notes (Slider_1..8 + Slider_Main) so touching a fader doesn't
    leak a note to FL Studio and play a sound. The fader *slide* (pitch bend) is intentionally
    left alone, so it still passes through for manual MIDI linking."""

    def __init__(self, mcuDevice: McuDevice):
        super().__init__(mcuDevice)

    def OnMidiMsg(self, event: FlMidiMsg):
        # The slider touch notes are contiguous: Slider_1 (0x68) .. Slider_Main (0x70).
        if event.midiId in (midi.MIDI_NOTEON, midi.MIDI_NOTEOFF) and \
                mcu_buttons.Slider_1 <= event.data1 <= mcu_buttons.Slider_Main:
            event.handled = True
            return event
        return super().OnMidiMsg(event)
