"""
User-editable settings for FLtouch.

Edit the values below to match your physical setup, then reload the scripts (or restart FL Studio)
for the change to take effect.
"""

from constants import mcu_extender_location
from constants import footswitch_action

# How extenders are positioned relative to the main unit (physical location).
#   mcu_extender_location.Left    All extenders to the left of the main unit   (EEEM)
#   mcu_extender_location.Right   All extenders to the right of the main unit  (MEEE)
#   mcu_extender_location.Middle  One extender to the left of the main unit,
#                                 all remaining extenders to its right         (EMEE)
# Note: extenders must be switched on in left-to-right order for FL studio to pick them up properly.
ExtenderPosition = mcu_extender_location.Middle                                                     

# What each foot pedal plugged into the back of your X-Touch does when you press it.
# There are two pedal jacks: "Foot SW 1" and "Foot SW 2". Set an action for each below.
#
# Available actions:
#   footswitch_action.TogglePlay       Start playback; press again to stop. (Same as the Play button.)
#   footswitch_action.ToggleRecord     Turn recording on; press again to turn it off. (Same as the Record button.)
#   footswitch_action.ToggleMetronome  Turn the metronome on; press again to turn it off.
#   footswitch_action.Passthrough      Do nothing here, so you can map the pedal yourself otherwise in FL Studio.
FootswitchAction1 = footswitch_action.TogglePlay     # Foot SW 1
FootswitchAction2 = footswitch_action.ToggleRecord   # Foot SW 2
