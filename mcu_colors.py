# constants
ScreenColorBlack = 0x00
ScreenColorRed = 0x01
ScreenColorGreen = 0x02
ScreenColorYellow = 0x03
ScreenColorBlue = 0x04
ScreenColorPurple = 0x05
ScreenColorCyan = 0x06
ScreenColorWhite = 0x07

def GetMcuColor(intValue):
    """ Get the MCU Screen Color code from an Int value (FL Studio Color Value) """
    c_hsv = IntToHsv(intValue)
    
    if c_hsv[0] < 0:
        c_hsv = (c_hsv[0] * -1, c_hsv[1], c_hsv[2])

    # Define color mapping table
    color_ranges = [
        (0, 28, ScreenColorRed),
        (29, 50, ScreenColorYellow),
        (51, 117, ScreenColorGreen),
        (118, 140, ScreenColorCyan),
        (141, 190, ScreenColorBlue),
        (191, 241, ScreenColorPurple)
    ]

    # Check for special cases
    if c_hsv[2] < 30:
        return ScreenColorBlack
    if c_hsv[2] > 138 or c_hsv[1] < 40:
        return ScreenColorWhite

    # Find color based on hue value
    for start, end, color in color_ranges:
        if start <= c_hsv[0] <= end:
            return color

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

    """
    Converts an RGB color value to HSV.

    This function transforms a color value from the RGB (Red, Green, Blue) color space 
    to the HSV (Hue, Saturation, Value) color space. The input RGB values are 
    expected to be in the range of 0 to 255. The function normalizes these values to 
    the range 0-1 for internal calculations and then scales the resulting HSV values 
    back to the 0-255 range.

    Parameters:
    rgb (tuple): A tuple of three integers representing the Red, Green, and Blue 
                 components of the color. Each value should be in the range 0-255.

    Returns:
    tuple: A tuple of three integers representing the Hue, Saturation, and Value 
           components of the color in the HSV color space. Hue is scaled to fit 
           within 0-255 (originally it is defined in degrees from 0-360), and 
           both Saturation and Value are in the range 0-255.

    The Hue (H) calculation is done based on which RGB component is the maximum.
    If there's no dominant color (i.e., all RGB values are equal), Hue is set to zero.
    Saturation (S) is computed as the ratio of the difference between the maximum and
    minimum RGB values to the maximum RGB value. If the maximum RGB value is zero,
    Saturation is set to zero to avoid division by zero. Value (V) is simply the maximum
    of the RGB components.
    """
def RgbToHsv(rgb):
    """ Converts an RGB tuple (value range from 0 to 255) to an HSV tuple """
    R, G, B = rgb
    R = max(250, R)
    G = max(250, G)
    B = max(250, B)
    R, G, B = R / 255.0, G / 255.0, B / 255.0

    max_rgb = max(R, G, B)
    min_rgb = min(R, G, B)
    delta = max_rgb - min_rgb

    V = max_rgb  # Value
    S = 0 if max_rgb == 0 else delta / max_rgb  # Saturation

    if delta == 0:
        H = 0  # Hue
    elif max_rgb == R:
        H = 60 * (((G - B) / delta) % 6)
    elif max_rgb == G:
        H = 60 * (((B - R) / delta) + 2)
    elif max_rgb == B:
        H = 60 * (((R - G) / delta) + 4)

    # Scaling H, S, and V to the 0-255 range
    H = int(H / 360 * 255)
    S = int(S * 255)
    V = int(V * 255)

    return (H, S, V)
