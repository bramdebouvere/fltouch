# fltouch V2

FL Studio MIDI scripts for the Behringer X-Touch + extender(s) (Mackie Control Universal) MIDI controllers, completely rewritten from the official scripts by Image-Line.

## Differences with the official scripts

- Support for multiple extenders (support for placement left/right and around the main unit)
- Support for colored scribble strips
- Support for controlling FX plugins on the selected mixer track
- Support for controlling FX plugin parameters (press select on an effect plugin)
- Support for controlling the Channel Rack
- Support for controlling Channel Rack plugin FX parameters (press select on a generator)
- Free mode has been removed, as it was replaced by the Channel Rack. If you still want to manually control plugins with "link to controller", you can use the faders in the plug-in mode to do so.
- Improved knob resolution and acceleration
- Improved jog wheel with automatic window focus
- Jog wheel will seek by default
- Auto channel selection when touching a fader
- Make use of the full scribble strip width
- Meter values are more accurate
- The clip led works when the signal is clipping
- Smoothing has been removed as it only caused delays
- Sliders now function in free control mode
- Changing the tempo using the jog wheel now works
- Added basic scrubbing functionality, hold shift for more accuracy
- Name/Value button can now be used to rename tracks, pressing Shift + Name/Value will change the track's color. Also works in the channel rack.
- The "Flip" button can now be used to bring up a menu with extra functions in certain modes.
- Encoder assignment buttons have been reordered to _Pan, Stereo, EQ, Sends, Effects, Free_ to match the hardware
- Various bugfixes and improvements

More improvements later...

## How to use

### Installation

1. This script uses the Mackie Control Universal (MCU) protocol. Your X-Touch and the extenders will need to be set to MCU mode. To do so,
    - Start with the device turned off
    - While holding down the SELECT button for channel 1, push the power switch
    - Rotate encoder 1 to set the mode to `MC`.
    - Rotate encoder 2 to select the interface to use (e.g. `USB`).
    - Pres the SELECT button for channel 1 to confirm settings.
    - The unit will now boot.
    - For more info, check out "*Step 3: Getting started*" in [the official quick-start guide](https://cdn-media.empowertribe.com/5f4ebaa5746d48b39c2bc317641de448/QSG_BE_0808-AAD_X-TOUCH_WW.pdf), p. 13.

2. Download all files in this repository *(Code -> Download ZIP)*. From the ZIP archive, copy all the files in the `fltouch-main` folder to your FL Studio Scripts folder, in a dedicated subfolder. Usually this would be:

- Windows: `%UserProfile%\Documents\Image-Line\Data\FL Studio\Settings\Hardware\fltouch`
- MacOS: `~/Image-Line/FL Studio/Settings/Hardware/fltouch`

3. In FL Studio's MIDI settings *(Options -> Midi settings)*, you'll find your "X-Touch" and "X-Touch-Ext" controllers. Set your X-Touch's MIDI channel to 102 and the extenders to 103, 104, ... and change the controller type to "FLtouch X-Touch" or "FLtouch X-Touch Extender" (depending on if the device is an extender or not).

![FL Studio Midi Settings Screen](https://user-images.githubusercontent.com/3641681/161856471-97810569-0ed5-4123-968a-68a11d295be2.png)

*If these instructions are unclear, you can find a more detailed guide by Zizzer Productions [here](https://www.zizzerproductions.com/post/make-behringer-universal-control-surface-work-with-fl-studio).*

### Settings

You can edit `settings.py` using a text editor to change settings such as extender location.

### Layout

You can print an overlay for this controller, courtesy of Bobby-Funk. The image must be printed 15.7956cm / 6.21875 inches wide in an A4 size.

<img width="1194" alt="271434055-cf50ff29-7763-49e1-a738-79fe292ccb69" src="https://github.com/bramdebouvere/fltouch/assets/3641681/375d51c0-6e41-424d-98f3-13a54432b747">

## Video

[![Using the Behringer X-Touch with FL Studio](https://img.youtube.com/vi/yJk2arJgTCM/0.jpg)](https://www.youtube.com/watch?v=yJk2arJgTCM)

## Older versions

For V1, which still uses parts of Image-Line's original code, please check https://github.com/bramdebouvere/fltouch/tree/legacy
