import unittest
from utilities.scribble_strip_text import StripSpacesIfOverWidth, CenterToWidth

# The scribble strip is 7 characters wide; tests use that as the width budget.
WIDTH = 7

class TestStripSpacesIfOverWidth(unittest.TestCase):
    def test_keeps_text_unchanged_when_it_fits(self):
        self.assertEqual(StripSpacesIfOverWidth('High Q', WIDTH), 'High Q')

    def test_keeps_text_unchanged_at_exact_width(self):
        self.assertEqual(StripSpacesIfOverWidth('Hi Pass', WIDTH), 'Hi Pass')

    def test_drops_spaces_when_over_width(self):
        # "High Pass" is 9 chars; dropping the space fits "HighPass" in 8 (still truncated by caller).
        self.assertEqual(StripSpacesIfOverWidth('High Pass', WIDTH), 'HighPass')

    def test_text_without_spaces_is_untouched(self):
        self.assertEqual(StripSpacesIfOverWidth('Frequency', WIDTH), 'Frequency')

class TestCenterToWidth(unittest.TestCase):
    def test_centers_shorter_text(self):
        # "Pan" (3) centred in 7 -> 2 leading, 2 trailing spaces.
        self.assertEqual(CenterToWidth('Pan', WIDTH), '  Pan  ')

    def test_returns_exact_width_for_short_text(self):
        self.assertEqual(len(CenterToWidth('Pan', WIDTH)), WIDTH)

    def test_leaves_exact_width_text_unchanged(self):
        self.assertEqual(CenterToWidth('-6.0 dB', WIDTH), '-6.0 dB')

    def test_truncates_longer_text_to_width(self):
        # "Frequency" (9) -> truncated to 7 characters.
        self.assertEqual(CenterToWidth('Frequency', WIDTH), 'Frequen')

    def test_truncates_to_exact_width(self):
        self.assertEqual(len(CenterToWidth('Frequency', WIDTH)), WIDTH)

# This allows running the tests from the command line
if __name__ == '__main__':
    unittest.main()
