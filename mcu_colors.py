# constants
ScreenColorBlack = 0x00
ScreenColorRed = 0x01
ScreenColorGreen = 0x02
ScreenColorYellow = 0x03
ScreenColorBlue = 0x04
ScreenColorPurple = 0x05
ScreenColorCyan = 0x06
ScreenColorWhite = 0x07

Hue = 0
Saturation = 1
Value = 2

def GetMcuColor(intValue):
    """ Get the MCU Screen Color code from an Int value (FL Studio Color Value) """
    c_hsv = IntToHsv(intValue)

    # Define color mapping table
    color_ranges = [
        (0, 69, ScreenColorYellow),
        (70, 119, ScreenColorGreen),
        (120, 149, ScreenColorCyan),
        (150, 199, ScreenColorBlue),
        (200, 309, ScreenColorPurple),
        (310, 399, ScreenColorRed)
    ]

    if c_hsv[Value] > 30 and c_hsv[Saturation] > 40:
        # Find color based on hue value
        for start, end, color in color_ranges:
            if start <= c_hsv[Hue] <= end:
                return color

    # Check for special cases
    if c_hsv[Value] < 30:
        return ScreenColorBlack
    if c_hsv[Value] > 138 or c_hsv[Saturation] < 40:
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

def RgbToHsv(rgb):
    R, G, B = rgb
    R, G, B = R / 255.0, G / 255.0, B / 255.0

    max_rgb = max(R, G, B)
    min_rgb = min(R, G, B)
    delta = max_rgb - min_rgb

    V = max_rgb  # Value
    S = 0 if max_rgb == 0 else (delta / max_rgb)  # Saturation

    if delta == 0:
         H = 0  # Hue
    elif max_rgb == R:
        H = 60 * (((G - B) / delta) % 6)
    elif max_rgb == G:
        H = 85 + 43 * (B-R)/delta
    elif max_rgb == B:
        H = 171 + 43 * (R-G)/delta

    S = int(S * 255)
    V = int(V * 255)

    return (int(H), int(S), int(V))
