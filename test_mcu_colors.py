import unittest
from mcu_colors import RgbToHsv

class TestRgbToHsv(unittest.TestCase):
    
    def test_black(self):
        self.assertEqual(RgbToHsv((0, 0, 0)), (0, 0, 0))

    def test_white(self):
        self.assertEqual(RgbToHsv((255, 255, 255)), (0, 0, 255))

    def test_red(self):
        self.assertEqual(RgbToHsv((255, 0, 0)), (0, 255, 255))

    def test_green(self):
        self.assertEqual(RgbToHsv((0, 255, 0)), (85, 255, 255))

    def test_blue(self):
        self.assertEqual(RgbToHsv((0, 0, 255)), (171, 255, 255))

    def test_custom_color(self):
        # Add a test for a custom RGB color
        self.assertEqual(RgbToHsv((int(229), int(229), int(21))), (60, 231, 229))  # yellow
        self.assertEqual(RgbToHsv((int(26), int(255), int(55))), (90, 229, 255))  # green
        self.assertEqual(RgbToHsv((int(94), int(154), int(174))), (138, 117, 174))  # cyan
        self.assertEqual(RgbToHsv((int(13), int(64), int(148))), (154, 232, 148)) # blue
        self.assertEqual(RgbToHsv((int(109), int(22), int(98))), (307, 203, 109))  # purple
        self.assertEqual(RgbToHsv((int(255), int(20), int(32))), (356, 235, 255))  # red

# This allows running the tests from the command line
if __name__ == '__main__':
    unittest.main()
