# Pure formatting helper for the Effects parameter view (no FL Studio imports, so it is unit-testable).

from utilities.scribble_strip_text import StripSpacesIfOverWidth

def FormatEffectParameterValue(paramValueString, paramValue, maxWidth):
    """
    Returns the parameters value as a string that can fit on the XTouch screen.

    Uses the plugin's own value string when it provides a non-empty one (getParamValueString is only
    supported by some plugins), otherwise falls back to the normalized value as a percentage (0-100%).

    When the result is longer than maxWidth, internal spaces are dropped so more of the value stays
    visible on the screen (e.g. "-42.6 dB" -> "-42.6dB"). The space is kept while it still fits.

    :param paramValueString: the plugin's value string (already transliterated to ASCII), or '' / None
    :param paramValue: the parameter's normalized value (0.0 - 1.0)
    :param maxWidth: the number of characters available on the scribble strip
    """
    text = paramValueString.strip() if paramValueString else ''
    if not text:
        text = str(round(paramValue * 100)) + '%'
    return StripSpacesIfOverWidth(text, maxWidth)
