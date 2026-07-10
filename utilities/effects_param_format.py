# Pure formatting helper for the Effects parameter view (no FL Studio imports, so it is unit-testable).

import re

from utilities.scribble_strip_text import StripSpacesIfOverWidth

# Matches a plain Hz value with a decimal fraction (e.g. "2000.3Hz", "2000.3 Hz", "2000.3hz").
# Requires a decimal point (integer Hz values need no change) and anchors "Hz" so compound units
# like "1.5kHz" or "2.0MHz" don't match (the char before "Hz" there is a letter, not \s or a digit).
_HZ_VALUE_PATTERN = re.compile(r'^(-?\d+\.\d+)\s*(Hz)$', re.IGNORECASE)

def RoundHzValue(text):
    """
    Rounds a plugin-reported plain-Hz value to a whole number, dropping decimal precision that
    isn't meaningful at these magnitudes (e.g. "2000.3Hz" -> "2000Hz"). Values with no decimal
    point, or with a compound unit (e.g. "1.5kHz"), are returned unchanged.

    :param text: the value string to check and possibly reformat
    """
    match = _HZ_VALUE_PATTERN.match(text)
    if not match:
        return text
    return str(round(float(match.group(1)))) + match.group(2)

def FormatEffectParameterValue(paramValueString, paramValue, maxWidth):
    """
    Returns the parameters value as a string that can fit on the XTouch screen.

    Uses the plugin's own value string when it provides a non-empty one (getParamValueString is only
    supported by some plugins), otherwise falls back to the normalized value as a percentage (0-100%).
    
    Plain Hz values with a decimal (e.g. "2000.3Hz") are rounded to a whole number first, since that
    precision isn't meaningful and often doesn't fit the screen.

    When the result is longer than maxWidth, internal spaces are dropped so more of the value stays
    visible on the screen (e.g. "-42.6 dB" -> "-42.6dB"). The space is kept while it still fits.

    :param paramValueString: the plugin's value string (already transliterated to ASCII), or '' / None
    :param paramValue: the parameter's normalized value (0.0 - 1.0)
    :param maxWidth: the number of characters available on the scribble strip
    """
    text = paramValueString.strip() if paramValueString else ''
    if text:
        text = RoundHzValue(text)
    else:
        text = str(round(paramValue * 100)) + '%'
    return StripSpacesIfOverWidth(text, maxWidth)
