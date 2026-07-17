"""
User-editable settings for FLtouch.

Edit the values below to match your physical setup, then reload the scripts (or restart FL Studio)
for the change to take effect.
"""

from constants import mcu_extender_location
from constants import footswitch_action

# Which side of the main X-Touch unit your X-Touch Extender(s) are connected on.
# Use mcu_extender_location.Left or mcu_extender_location.Right.
ExtenderPosition = mcu_extender_location.Left

# What each foot pedal plugged into the back of your X-Touch does when you press it.
# There are two pedal jacks: "Foot SW 1" and "Foot SW 2". Set an action for each below.
#
# Available actions:
#   footswitch_action.TogglePlay       Start playback; press again to stop. (Same as the Play button.)
#   footswitch_action.ToggleRecord     Turn recording on; press again to turn it off. (Same as the Record button.)
#   footswitch_action.ToggleMetronome  Turn the metronome (click) on; press again to turn it off.
#   footswitch_action.Passthrough      Do nothing here, so you can map the pedal yourself in FL Studio's MIDI settings.
FootswitchAction1 = footswitch_action.TogglePlay     # Foot SW 1
FootswitchAction2 = footswitch_action.ToggleRecord   # Foot SW 2
