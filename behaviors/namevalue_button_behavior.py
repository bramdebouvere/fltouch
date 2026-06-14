import midi
import transport
from behaviors.mcu_base_behavior import McuBaseBehavior
from behaviors.mcu_base_screen_behavior import McuBaseScreenBehavior
from constants import mcu_extender_location
from device_hal import mcu_buttons
from device_hal.mcu_device import McuDevice
from utilities.button_manager import ButtonManager
from utilities.track_banking_manager import TrackBankingManager


class NameValueButtonBehavior(McuBaseBehavior):
    """Handles the Name/Value button.

    Normal press: triggers rename (FPT_F2).
    Shift + press: toggles extender position between left and right.
    """

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
            if ButtonManager.ShiftPressed:
                new_pos = self._trackBankingManager.ToggleExtenderPosition()
                self._screenBehavior.OnSendTempMsg('Extenders on ' + mcu_extender_location.Names[new_pos])
            else:
                transport.globalTransport(midi.FPT_F2, 2, event.pmeFlags, 8)

        event.handled = True
        return event
