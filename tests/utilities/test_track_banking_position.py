import sys
import types
import unittest

# TrackBankingManager imports FL Studio modules (`device`, `midi`, `mixer`) and the HAL
# `McuDevice`, none of which exist outside FL. Stub them in sys.modules BEFORE importing.
# We AUGMENT rather than replace existing stubs, so running under `unittest discover`
# (shared sys.modules) never clobbers another test module's `midi`/`device_hal.mcu_device`.

def _stub_module(name):
    mod = sys.modules.get(name)
    if mod is None:
        mod = types.ModuleType(name)
        sys.modules[name] = mod
    return mod


def _install_fl_stubs():
    device = _stub_module('device')
    if not hasattr(device, '_receiverCount'):
        device._receiverCount = 0
    device.dispatchReceiverCount = lambda: sys.modules['device']._receiverCount
    device.dispatch = lambda n, msg: None

    midi = _stub_module('midi')
    if not hasattr(midi, 'MIDI_NOTEON'):
        midi.MIDI_NOTEON = 0x90

    mixer = _stub_module('mixer')
    if not hasattr(mixer, '_trackCount'):
        mixer._trackCount = 200
    mixer.trackCount = lambda: sys.modules['mixer']._trackCount

    mcu_device = _stub_module('device_hal.mcu_device')
    if not hasattr(mcu_device, 'McuDevice'):
        mcu_device.McuDevice = type('McuDevice', (), {})


_install_fl_stubs()

import device
import settings
from constants import mcu_extender_location
from constants import mcu_constants
from device_hal import mcu_buttons
from utilities.track_banking_manager import TrackBankingManager

class FakeMcuDevice:
    """Records the absolute first-track values the main unit pushes to each extender."""
    def __init__(self, isExtender=False):
        self.isExtender = isExtender
        self.pushes = {}  # extenderIndex -> firstTrack

    def SetFirstTrackOnExtender(self, extenderIndex, firstTrack):
        self.pushes[extenderIndex] = firstTrack


class TestTrackBankingPosition(unittest.TestCase):
    """
    Verifies the physical-fader -> mixer-track offset math for every extender layout.
    The rig is always one contiguous, left-to-right block of tracks; only the main unit's
    slot in that block changes (Left = far right, Right = far left, Middle = second from left).
    """

    def setUp(self):
        self._origPos = settings.ExtenderPosition
        self._origCount = device._receiverCount

    def tearDown(self):
        settings.ExtenderPosition = self._origPos
        device._receiverCount = self._origCount

    def _manager(self, position, extenderCount, isExtender=False):
        # ExtenderPosition is read in the constructor, so set it first.
        settings.ExtenderPosition = position
        device._receiverCount = extenderCount
        dev = FakeMcuDevice(isExtender)
        return TrackBankingManager(dev), dev

    # ---- Named cases (with the leftmost track fixed at 0) ----

    def test_left_two_extenders_matches_original_behavior(self):
        # E E M : extenders lowest, main on the far right.
        mgr, dev = self._manager(mcu_extender_location.Left, 2)
        mgr.SetFirstTrackIndex(0)
        self.assertEqual(dev.pushes, {0: 0, 1: mcu_constants.TrackCount})
        self.assertEqual(mgr.FirstTrack, 2 * mcu_constants.TrackCount)
        self.assertEqual(mgr.GetFirstTrack(), 0)

    def test_right_two_extenders_matches_original_behavior(self):
        # M E E : main lowest, on the far left.
        mgr, dev = self._manager(mcu_extender_location.Right, 2)
        mgr.SetFirstTrackIndex(0)
        self.assertEqual(dev.pushes, {0: mcu_constants.TrackCount, 1: 2 * mcu_constants.TrackCount})
        self.assertEqual(mgr.FirstTrack, 0)
        self.assertEqual(mgr.GetFirstTrack(), 0)

    def test_middle_two_extenders(self):
        # E M E : one extender left of the main, one to the right.
        mgr, dev = self._manager(mcu_extender_location.Middle, 2)
        mgr.SetFirstTrackIndex(0)
        self.assertEqual(dev.pushes, {0: 0, 1: 2 * mcu_constants.TrackCount})  # ext0 = slot 0, ext1 = slot 2
        self.assertEqual(mgr.FirstTrack, mcu_constants.TrackCount)              # main = slot 1
        self.assertEqual(mgr.GetFirstTrack(), 0)

    def test_middle_three_extenders(self):
        # E M E E : one extender left, two to the right.
        mgr, dev = self._manager(mcu_extender_location.Middle, 3)
        mgr.SetFirstTrackIndex(0)
        self.assertEqual(dev.pushes, {0: 0, 1: 2 * mcu_constants.TrackCount, 2: 3 * mcu_constants.TrackCount})
        self.assertEqual(mgr.FirstTrack, mcu_constants.TrackCount)
        self.assertEqual(mgr.GetFirstTrack(), 0)

    def test_middle_one_extender_equals_left(self):
        # With a single extender, Middle places it on the left (E M), same as Left.
        mgr, dev = self._manager(mcu_extender_location.Middle, 1)
        mgr.SetFirstTrackIndex(0)
        self.assertEqual(dev.pushes, {0: 0})
        self.assertEqual(mgr.FirstTrack, mcu_constants.TrackCount)
        self.assertEqual(mgr.GetFirstTrack(), 0)

    # ---- Invariant across every layout / extender count ----

    def test_blocks_are_contiguous_and_left_edge_correct(self):
        LEFT_EDGE = 5
        for position in (mcu_extender_location.Left,
                         mcu_extender_location.Right,
                         mcu_extender_location.Middle):
            for extenderCount in (0, 1, 2, 3):
                mgr, dev = self._manager(position, extenderCount)
                mgr.SetFirstTrackIndex(LEFT_EDGE)
                blockStarts = sorted(list(dev.pushes.values()) + [mgr.FirstTrack])
                expected = [LEFT_EDGE + mcu_constants.TrackCount * k for k in range(extenderCount + 1)]
                msg = 'position=%d extenderCount=%d' % (position, extenderCount)
                # Every unit shows a distinct 8-track block; together they tile the array with no gaps.
                self.assertEqual(blockStarts, expected, msg)
                # GetFirstTrack always reports the true global-left track.
                self.assertEqual(mgr.GetFirstTrack(), LEFT_EDGE, msg)

    # ---- Bank navigation still works with the main in the middle ----

    def test_middle_bank_right_shifts_whole_array_by_one_unit(self):
        mgr, dev = self._manager(mcu_extender_location.Middle, 2)
        mgr.SetFirstTrackIndex(0)
        mgr.HandleBankButton(mcu_buttons.FaderBankRight)  # +8
        self.assertEqual(mgr.GetFirstTrack(), mcu_constants.TrackCount)
        self.assertEqual(dev.pushes, {0: mcu_constants.TrackCount, 1: 3 * mcu_constants.TrackCount})
        self.assertEqual(mgr.FirstTrack, 2 * mcu_constants.TrackCount)

    # ---- Extenders never compute layout; they store the absolute value handed to them ----

    def test_extender_stores_absolute_value_and_pushes_nothing(self):
        mgr, dev = self._manager(mcu_extender_location.Middle, 2, isExtender=True)
        mgr.SetFirstTrackIndex(3 * mcu_constants.TrackCount)
        self.assertEqual(mgr.FirstTrack, 3 * mcu_constants.TrackCount)
        self.assertEqual(dev.pushes, {})


if __name__ == '__main__':
    unittest.main()
