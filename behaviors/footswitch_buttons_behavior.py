import midi
import transport

import settings
from behaviors.mcu_base_behavior import McuBaseBehavior
from constants import footswitch_action
from device_hal import mcu_buttons
from device_hal.mcu_device import McuDevice

class FootswitchButtonsBehavior(McuBaseBehavior):
    """Handles the X-Touch's two rear-panel footswitch jacks.

    Each jack sends an MCU Note On (Foot SW 1 = 0x66, Foot SW 2 = 0x67) when
    pressed. The action performed by each jack is user-configurable via
    settings.FootswitchAction1 / FootswitchAction2.
    """

    # Map action to FTP command.
    _ACTION_TO_TRANSPORT = {
        footswitch_action.TogglePlay:      (midi.FPT_Play, 2),
        footswitch_action.ToggleRecord:    (midi.FPT_Record, 2),
        footswitch_action.ToggleMetronome: (midi.FPT_Metronome, 1),
    }

    def __init__(self, mcuDevice: McuDevice):
        super().__init__(mcuDevice)
        # Read configured actions from settings
        self._actions = {
            mcu_buttons.Footswitch_1: settings.FootswitchAction1,
            mcu_buttons.Footswitch_2: settings.FootswitchAction2,
        }

    def OnMidiMsg(self, event):
        if event.midiId == midi.MIDI_NOTEON and event.data1 in self._actions:

            action = self._ACTION_TO_TRANSPORT.get(self._actions[event.data1])

            if action is None:
                # Passthrough -> leave unhandled so the FL still receives the note.
                return super().OnMidiMsg(event)
            
            # A footswitch is a momentary switch: one tap sends press (velocity > 0)
            # then release (velocity 0). Act on the press only so each tap toggles once.
            if event.data2 > 0:
                command, value = action
                transport.globalTransport(command, value, event.pmeFlags)
            
            event.handled = True
            return event
        return super().OnMidiMsg(event)
