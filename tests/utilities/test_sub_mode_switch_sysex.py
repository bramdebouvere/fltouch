import unittest
from utilities.sub_mode_switch_sysex import EncodeSubModeSwitch, DecodeSubModeSwitch

class TestSubModeSwitchRoundTrip(unittest.TestCase):
    def test_round_trips_with_no_data(self):
        for key in range(4):
            self.assertEqual(DecodeSubModeSwitch(EncodeSubModeSwitch(key, None)), (key, None))

    def test_round_trips_with_small_data(self):
        self.assertEqual(DecodeSubModeSwitch(EncodeSubModeSwitch(1, 0)), (1, 0))
        self.assertEqual(DecodeSubModeSwitch(EncodeSubModeSwitch(2, 1)), (2, 1))

    def test_round_trips_with_data_too_large_for_5_bits(self):
        # 31 was the old NOTEON-only ceiling; well above it now that data is carried via SysEx.
        self.assertEqual(DecodeSubModeSwitch(EncodeSubModeSwitch(3, 8191)), (3, 8191))

    def test_round_trips_with_max_value(self):
        self.assertEqual(DecodeSubModeSwitch(EncodeSubModeSwitch(0, 2_097_151)), (0, 2_097_151))

    def test_data_zero_is_distinct_from_no_data(self):
        # channel 0 is a real, valid channel index -- must not collapse to "no data".
        withZero = DecodeSubModeSwitch(EncodeSubModeSwitch(1, 0))
        withNone = DecodeSubModeSwitch(EncodeSubModeSwitch(1, None))
        self.assertEqual(withZero, (1, 0))
        self.assertEqual(withNone, (1, None))
        self.assertNotEqual(withZero, withNone)

class TestDecodeSubModeSwitchRejectsNonMatchingBytes(unittest.TestCase):
    def test_rejects_wrong_sysex_id(self):
        encoded = bytearray(EncodeSubModeSwitch(1, 5))
        encoded[1] = 0x02  # a different sysex id
        self.assertIsNone(DecodeSubModeSwitch(bytes(encoded)))

    def test_rejects_wrong_length(self):
        self.assertIsNone(DecodeSubModeSwitch(bytes([0xF0, 0x01, 0x00, 0x00, 0xF7])))

    def test_rejects_missing_terminator(self):
        encoded = bytearray(EncodeSubModeSwitch(1, 5))
        encoded[-1] = 0x00
        self.assertIsNone(DecodeSubModeSwitch(bytes(encoded)))

    def test_rejects_missing_leading_byte(self):
        encoded = bytearray(EncodeSubModeSwitch(1, 5))
        encoded[0] = 0x00
        self.assertIsNone(DecodeSubModeSwitch(bytes(encoded)))

    def test_rejects_empty_bytes(self):
        self.assertIsNone(DecodeSubModeSwitch(b''))

if __name__ == '__main__':
    unittest.main()
