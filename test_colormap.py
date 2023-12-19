import unittest
from mcu_colors import GetMcuColor,ScreenColorBlack,ScreenColorRed,ScreenColorGreen,ScreenColorYellow,ScreenColorBlue,ScreenColorPurple,ScreenColorCyan,ScreenColorWhite 

# test specific code to pack rgb back into int
def RgbToInt(rgb):
    R,G,B = rgb
    int_value = ((R&255) << 16)
    int_value |= ((G&255) << 8)
    int_value |= (B&255)
    return int_value

class TestGetMcuColor(unittest.TestCase):
    
    def test_black(self):
        self.assertEqual(GetMcuColor(RgbToInt((0, 0, 0))), ScreenColorBlack)

    def test_white(self):
        self.assertEqual(GetMcuColor(RgbToInt((255, 255, 255))), ScreenColorWhite)

    def test_custom_color(self):
        # Add a test for a custom RGB color
        self.assertEqual(GetMcuColor(RgbToInt((int(229), int(229), int(21)))), ScreenColorYellow)  # yellow
        self.assertEqual(GetMcuColor(RgbToInt((int(26), int(255), int(55)))), ScreenColorGreen)  # green
        self.assertEqual(GetMcuColor(RgbToInt((int(94), int(154), int(174)))), ScreenColorCyan)  # cyan
        self.assertEqual(GetMcuColor(RgbToInt((int(13), int(64), int(148)))), ScreenColorBlue) # blue
        self.assertEqual(GetMcuColor(RgbToInt((int(109), int(22), int(98)))), ScreenColorPurple)  # purple
        self.assertEqual(GetMcuColor(RgbToInt((int(255), int(20), int(32)))), ScreenColorRed)  # red

# This allows running the tests from the command line
if __name__ == '__main__':
    unittest.main()
