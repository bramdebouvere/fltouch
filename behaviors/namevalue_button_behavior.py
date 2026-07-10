import midi
import transport
from behaviors.mcu_base_behavior import McuBaseBehavior
from behaviors.mcu_base_screen_behavior import McuBaseScreenBehavior
from device_hal import mcu_buttons
from device_hal.mcu_device import McuDevice
from utilities.track_banking_manager import TrackBankingManager

class NameValueButtonBehavior(McuBaseBehavior):
    """Handles the Name/Value button: triggers rename (F2)"""

    def __init__(self, mcuDevice, trackBankingManager, screenBehavior):
        super().__init__(mcuDevice)
        self._trackBankingManager = trackBankingManager
        self._screenBehavior = screenBehavior

    def OnMidiMsg(self, event):
        if event.midiId != midi.MIDI_NOTEON:
            return super().OnMidiMsg(event)
        if event.data1 != mcu_buttons.NameValue:
            return super().OnMidiMsg(event)

        if event.data2 > 0:
            transport.globalTransport(midi.FPT_F2, 2, event.pmeFlags, 8)

        event.handled = True
        return event
