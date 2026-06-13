"""Utility for tracking global button state."""

class _ButtonManager:
    """Tracks persistent button states for the MCU controller."""

    def __init__(self):
        self._shiftPressed = False
        self._jogsource = 0

    @property
    def ShiftPressed(self) -> bool:
        """Returns True when the shift button is currently pressed."""
        return self._shiftPressed

    @ShiftPressed.setter
    def ShiftPressed(self, value: bool):
        self._shiftPressed = bool(value)

    @property
    def JogSource(self) -> int:
        """Current jog source button ID (0 when none)."""
        return self._jogsource

    @JogSource.setter
    def JogSource(self, value: int):
        self._jogsource = value

# Singleton instance of the ButtonManager that can be imported and used across the project
ButtonManager = _ButtonManager()
