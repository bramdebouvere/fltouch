import sys
import types
import unittest

# Stub `mixer` in sys.modules BEFORE importing the helper, so it binds to this bare module instead
# of the site-packages FL stub (whose import can collide with another test's minimal `midi` stub
# under `unittest discover`). Augment rather than replace an existing stub.

def _stub_module(name):
    mod = sys.modules.get(name)
    if mod is None:
        mod = types.ModuleType(name)
        sys.modules[name] = mod
    return mod

mixer = _stub_module('mixer')

from constants import mcu_constants
from utilities.effects_slot_count import GetEffectsSlotCount

class TestEffectsSlotCount(unittest.TestCase):
    """Verifies the FL 26.2 mixer.getSlotCount feature detection and fallback."""

    def setUp(self):
        # Start each test without the API so another test can't leak its fake into this one.
        if hasattr(mixer, 'getSlotCount'):
            delattr(mixer, 'getSlotCount')

    def tearDown(self):
        if hasattr(mixer, 'getSlotCount'):
            delattr(mixer, 'getSlotCount')

    def test_falls_back_to_default_without_api(self):
        self.assertEqual(GetEffectsSlotCount(3), mcu_constants.EffectsSlotCount)

    def test_per_track_value_is_returned_unchanged(self):
        mixer.getSlotCount = lambda track: 25 # type: ignore
        self.assertEqual(GetEffectsSlotCount(7), 25)

    def test_low_count_is_returned_unchanged(self):
        # FL 26.2 allows as few as 1 slot per track.
        mixer.getSlotCount = lambda track: 1 # type: ignore
        self.assertEqual(GetEffectsSlotCount(2), 1)

    def test_default_count_is_returned_unchanged(self):
        mixer.getSlotCount = lambda track: 10 # type: ignore
        self.assertEqual(GetEffectsSlotCount(2), 10)

    def test_runtime_error_falls_back_to_default(self):
        def getSlotCount(track):
            raise RuntimeError('Index out of range')

        mixer.getSlotCount = getSlotCount # type: ignore
        self.assertEqual(GetEffectsSlotCount(300), mcu_constants.EffectsSlotCount)

if __name__ == '__main__':
    unittest.main()
