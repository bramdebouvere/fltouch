# constants
ScreenColorBlack = 0x00
ScreenColorRed = 0x01
ScreenColorGreen = 0x02
ScreenColorYellow = 0x03
ScreenColorBlue = 0x04
ScreenColorPink = 0x05
ScreenColorCyan = 0x06
ScreenColorWhite = 0x07

# derived from the color conversion code by djnaoki-mrn (https://github.com/djnaoki-mrn/)


def GetMcuColor(intValue):
    """ Get the MCU Screen Color code from an Int value (FL Studio Color Value) """
    c_hsv = IntToHsv(intValue)

    if c_hsv[0] < 0:
        c_hsv = (c_hsv[0] * -1, c_hsv[1], c_hsv[2])

    if c_hsv[2] > 30 and c_hsv[1] > 40:
        if (c_hsv[0] >= 0 and c_hsv[0] < 28) or (c_hsv[0] > 242 and c_hsv[0] <= 255):  # red
            return ScreenColorRed
        if (c_hsv[0] > 28 and c_hsv[0] < 53):  # yellow
            return ScreenColorYellow
        if (c_hsv[0] > 50 and c_hsv[0] < 117):  # green
            return ScreenColorGreen
        if (c_hsv[0] > 118 and c_hsv[0] < 140):  # cyan
            return ScreenColorCyan
        if (c_hsv[0] > 141 and c_hsv[0] < 190):  # blue
            return ScreenColorBlue
        if (c_hsv[0] > 191 and c_hsv[0] < 241):  # pink
            return ScreenColorPink

    if c_hsv[2] < 30:
        return ScreenColorBlack
    if c_hsv[2] > 138 or c_hsv[1] < 40:
        return ScreenColorWhite
    return ScreenColorWhite


def IntToHsv(intValue):
    """ Convert an FL Studio Color Value (Int) to HSV """
    return(RgbToHsv(IntToRGB(intValue)))


def IntToRGB(intValue):
    """ Convert an FL Studio Color Value (Int) to RGB """
    blue = intValue & 255
    green = (intValue >> 8) & 255
    red = (intValue >> 16) & 255
    return (red, green, blue)


def RgbToHsv(RGB):
    """ Converts an integer RGB tuple (value range from 0 to 255) to an HSV tuple """
    # Unpack the tuple for readability
    R, G, B = RGB
    # Compute the H value by finding the maximum of the RGB values
    RGB_Max = max(RGB)
    RGB_Min = min(RGB)
    # Compute the value
    V = RGB_Max
    if V == 0:
        H = S = 0
        return (H, S, V)
    # Compute the saturation value
    S = 255 * (RGB_Max - RGB_Min) // V
    if S == 0:
        H = 0
        return (H, S, V)
    # Compute the Hue
    if RGB_Max == R:
        H = 0 + 43*(G - B)//(RGB_Max - RGB_Min)
    elif RGB_Max == G:
        H = 85 + 43*(B - R)//(RGB_Max - RGB_Min)
    else:  # RGB_MAX == B
        H = 171 + 43*(R - G)//(RGB_Max - RGB_Min)
    return (H, S, V)
