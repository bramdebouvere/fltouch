import unittest
from utilities.effects_param_format import FormatEffectParameterValue

# The scribble strip is 7 characters wide; tests use that as the width budget.
WIDTH = 7

class TestFormatParamValue(unittest.TestCase):

    def test_uses_value_string_when_present(self):
        self.assertEqual(FormatEffectParameterValue('-6.0 dB', 0.5, WIDTH), '-6.0 dB')

    def test_strips_value_string(self):
        self.assertEqual(FormatEffectParameterValue('  100 Hz ', 0.5, WIDTH), '100 Hz')

    def test_empty_string_falls_back_to_percentage(self):
        self.assertEqual(FormatEffectParameterValue('', 0.5, WIDTH), '50%')

    def test_none_falls_back_to_percentage(self):
        self.assertEqual(FormatEffectParameterValue(None, 0.0, WIDTH), '0%')

    def test_whitespace_only_falls_back_to_percentage(self):
        self.assertEqual(FormatEffectParameterValue('   ', 1.0, WIDTH), '100%')

    def test_percentage_is_rounded(self):
        self.assertEqual(FormatEffectParameterValue('', 0.25, WIDTH), '25%')
        self.assertEqual(FormatEffectParameterValue('', 0.999, WIDTH), '100%')

    def test_keeps_space_when_it_fits(self):
        # "-6.0 dB" is exactly 7 chars, so the space stays.
        self.assertEqual(FormatEffectParameterValue('-6.0 dB', 0.5, WIDTH), '-6.0 dB')

    def test_drops_internal_spaces_when_over_width(self):
        # "-42.6 dB" is 8 chars; dropping the space fits "-42.6dB" in 7.
        self.assertEqual(FormatEffectParameterValue('-42.6 dB', 0.5, WIDTH), '-42.6dB')

    def test_drops_all_spaces_when_still_over_width(self):
        # Even when stripping does not fully fit, removing spaces keeps more meaningful characters.
        self.assertEqual(FormatEffectParameterValue('-42.65 dB', 0.5, WIDTH), '-42.65dB')

    def test_rounds_decimal_hz_value(self):
        self.assertEqual(FormatEffectParameterValue('2000.3Hz', 0.5, WIDTH), '2000Hz')

    def test_rounds_decimal_hz_value_with_space(self):
        self.assertEqual(FormatEffectParameterValue('2000.3 Hz', 0.5, WIDTH), '2000Hz')

    def test_integer_hz_value_unchanged(self):
        self.assertEqual(FormatEffectParameterValue('500Hz', 0.5, WIDTH), '500Hz')

    def test_rounded_hz_value_fits_width(self):
        # "20000.3Hz" is 9 chars; rounding to "20000Hz" fits exactly in 7.
        self.assertEqual(FormatEffectParameterValue('20000.3Hz', 0.5, WIDTH), '20000Hz')

    def test_lowercase_hz_suffix_is_rounded_and_case_preserved(self):
        self.assertEqual(FormatEffectParameterValue('2000.3hz', 0.5, WIDTH), '2000hz')

    def test_negative_hz_value_is_rounded(self):
        self.assertEqual(FormatEffectParameterValue('-42.65Hz', 0.5, WIDTH), '-43Hz')

    def test_khz_value_is_left_unchanged(self):
        # Compound units are excluded: a kHz decimal represents up to 100s of Hz of precision.
        self.assertEqual(FormatEffectParameterValue('1.5kHz', 0.5, WIDTH), '1.5kHz')

    def test_non_hz_decimal_value_unchanged(self):
        self.assertEqual(FormatEffectParameterValue('3.5 ms', 0.5, WIDTH), '3.5 ms')

    def test_non_numeric_value_unchanged(self):
        self.assertEqual(FormatEffectParameterValue('Off', 0.5, WIDTH), 'Off')
        self.assertEqual(FormatEffectParameterValue('High Pass', 0.5, WIDTH), 'HighPass')

# This allows running the tests from the command line
if __name__ == '__main__':
    unittest.main()
