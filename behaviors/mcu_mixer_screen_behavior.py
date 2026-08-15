import midi

from behaviors.mcu_base_screen_behavior import McuBaseScreenBehavior

class McuMixerScreenBehavior(McuBaseScreenBehavior):
    """Behavior for the screen."""

    def OnEnable(self):
        super().OnEnable()
        self.RenderScreen()

    def OnRefresh(self, flags):
        super().OnRefresh(flags)

        # Update screen when mixer display changes
        if flags & midi.HW_Dirty_Mixer_Display:
            self.RenderScreen()

    def RenderScreen(self):
        """Update the screen content based on the current state of the mixer."""

        self.RenderTrackNumbers(row=0)
        self.RenderTrackNames(row=1)
        self.RenderTrackColors()
