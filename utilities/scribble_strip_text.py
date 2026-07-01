# Pure text-shaping helpers for the fixed-width scribble strip (no FL Studio imports, so they are unit-testable).

def StripSpacesIfOverWidth(text: str, maxWidth: int) -> str:
    """
    Drop internal spaces when text is longer than maxWidth, so more of it stays visible on the
    fixed-width scribble strip (e.g. "High Pass" -> "HighPass", "-42.6 dB" -> "-42.6dB"). Spaces are
    kept while the text still fits. This is best-effort: the result may still exceed maxWidth, so the
    caller is still responsible for centering/truncating to width (see center_to_width).

    :param text: the text to shape
    :param maxWidth: the number of characters available on the scribble strip
    """
    if len(text) > maxWidth:
        text = text.replace(' ', '')
    return text

def CenterToWidth(text: str, width: int) -> str:
    """
    Lay text out across a strip exactly `width` characters wide: shorter text is padded with spaces on
    both sides (centred), longer text is truncated. Always returns exactly `width` characters.

    :param text: the text to lay out
    :param width: the number of characters on the scribble strip
    """
    return text.center(width)[:width]
