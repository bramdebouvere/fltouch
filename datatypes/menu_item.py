from typing import Callable

class MenuItem:
    """
    Selectable entry in a flip menu.

    label:    scribble-strip label (max 7 chars, one strip)
    execute:  zero-arg callable run when this item's SELECT is pressed.
              Returns None on success (or when there's nothing to report),
              or a short message to flash on screen temporarily
    color:    FL Studio color int for the scribble strip
    getValue: optional zero-arg callable returning the bottom-row status text (str) for this item,
              e.g. an on/off state, a value or a name. The screen centers/truncates it to the strip
              width, so return the plain text. None for an item with no status to show (bottom row
              stays blank).
    """

    def __init__(self, label: str, execute: Callable[[], str | None], color: int,
                 getValue: Callable[[], str] | None = None):
        self.label = label
        self.execute = execute
        self.color = color
        self.getValue = getValue
