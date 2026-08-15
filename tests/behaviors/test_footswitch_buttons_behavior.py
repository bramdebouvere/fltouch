import sys
import types
import unittest

# The behavior imports FL Studio modules (`midi`, `transport`) and the HAL
# `McuDevice`, none of which exist outside FL. Stub them in sys.modules BEFORE
# importing the behavior so the module (and its class-level FPT table) load.


def _install_fl_stubs():
    midi = types.ModuleType('midi')
    midi.MIDI_NOTEON = 0x90
    midi.FPT_Play = 10
    midi.FPT_Record = 12
    midi.FPT_Metronome = 34
    sys.modules['midi'] = midi

    transport = types.ModuleType('transport')
    transport.calls = []
    transport.globalTransport = lambda command, value, flags=None: transport.calls.append((command, value, flags))
    sys.modules['transport'] = transport

    # Replace only device_hal.mcu_device (which pulls in FL modules); the rest of
    # the device_hal package (mcu_buttons) is pure Python and loads for real.
    mcu_device = types.ModuleType('device_hal.mcu_device')
    mcu_device.McuDevice = type('McuDevice', (), {})
    sys.modules['device_hal.mcu_device'] = mcu_device


_install_fl_stubs()

import midi
import transport
import settings
from behaviors.footswitch_buttons_behavior import FootswitchButtonsBehavior
from constants import footswitch_action
from device_hal import mcu_buttons


class FakeEvent:
    """Minimal stand-in for FlMidiMsg."""
    def __init__(self, midiId, data1, data2):
        self.midiId = midiId
        self.data1 = data1
        self.data2 = data2
        self.pmeFlags = 0
        self.handled = False


class TestFootswitchButtonsBehavior(unittest.TestCase):

    def setUp(self):
        transport.calls = []
        self._orig = (settings.FootswitchAction1, settings.FootswitchAction2)

    def tearDown(self):
        settings.FootswitchAction1, settings.FootswitchAction2 = self._orig

    def _behavior(self, action1, action2=footswitch_action.Passthrough):
        settings.FootswitchAction1 = action1
        settings.FootswitchAction2 = action2
        return FootswitchButtonsBehavior(None)

    def test_press_toggle_play_calls_global_transport(self):
        behavior = self._behavior(footswitch_action.TogglePlay)
        event = FakeEvent(midi.MIDI_NOTEON, mcu_buttons.Footswitch_1, 127)
        behavior.OnMidiMsg(event)
        self.assertEqual(transport.calls, [(midi.FPT_Play, 2, 0)])
        self.assertTrue(event.handled)

    def test_toggle_record_maps_to_fpt_record(self):
        behavior = self._behavior(footswitch_action.ToggleRecord)
        behavior.OnMidiMsg(FakeEvent(midi.MIDI_NOTEON, mcu_buttons.Footswitch_1, 127))
        self.assertEqual(transport.calls, [(midi.FPT_Record, 2, 0)])

    def test_toggle_metronome_maps_to_fpt_metronome(self):
        # Metronome mirrors the Metronome button, which fires with value 1 (not 2).
        behavior = self._behavior(footswitch_action.ToggleMetronome)
        behavior.OnMidiMsg(FakeEvent(midi.MIDI_NOTEON, mcu_buttons.Footswitch_1, 127))
        self.assertEqual(transport.calls, [(midi.FPT_Metronome, 1, 0)])

    def test_release_triggers_nothing_but_is_consumed(self):
        behavior = self._behavior(footswitch_action.TogglePlay)
        event = FakeEvent(midi.MIDI_NOTEON, mcu_buttons.Footswitch_1, 0)  # velocity 0 = released
        behavior.OnMidiMsg(event)
        self.assertEqual(transport.calls, [])   # no toggle on release
        self.assertTrue(event.handled)          # but the note is still owned

    def test_passthrough_leaves_event_unhandled(self):
        behavior = self._behavior(footswitch_action.Passthrough)
        event = FakeEvent(midi.MIDI_NOTEON, mcu_buttons.Footswitch_1, 127)
        behavior.OnMidiMsg(event)
        self.assertEqual(transport.calls, [])
        self.assertFalse(event.handled)         # DAW can still receive the note

    def test_second_jack_uses_its_own_action(self):
        behavior = self._behavior(footswitch_action.Passthrough, footswitch_action.ToggleRecord)
        behavior.OnMidiMsg(FakeEvent(midi.MIDI_NOTEON, mcu_buttons.Footswitch_2, 127))
        self.assertEqual(transport.calls, [(midi.FPT_Record, 2, 0)])

    def test_unrelated_note_is_ignored(self):
        behavior = self._behavior(footswitch_action.TogglePlay)
        event = FakeEvent(midi.MIDI_NOTEON, mcu_buttons.Play, 127)  # a real transport button, not a footswitch
        behavior.OnMidiMsg(event)
        self.assertEqual(transport.calls, [])
        self.assertFalse(event.handled)

    def test_non_noteon_is_ignored(self):
        behavior = self._behavior(footswitch_action.TogglePlay)
        event = FakeEvent(0xB0, mcu_buttons.Footswitch_1, 127)  # control change, not note on
        behavior.OnMidiMsg(event)
        self.assertEqual(transport.calls, [])
        self.assertFalse(event.handled)


if __name__ == '__main__':
    unittest.main()
