# fltouch

FL Studio MIDI scripts for the Behringer X-Touch + extender(s) (Mackie Control Universal) MIDI controllers, based on the official scripts by Image-Line.

## Differences with the official scripts

- Support for multiple extenders
- Support for colored scribble strips
- Improved knob resolution and acceleration
- Improved jog wheel with automatic window focus
- Jog wheel will seek by default
- Auto channel selection when touching a fader
- Make use of the full scribble strip width
- Meter values are more accurate
- The clip led works when the signal is clipping
- Smoothing is disabled by default
- Sliders now function in free control mode
- Changing the tempo using the jog wheel now works
- Added basic scrubbing functionality, hold shift for more accuracy
- Name/Value button can now be used to rename tracks
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
    - For more info, check out "*Step 3: Getting started*" in [the official quick-start guide](https://mediadl.musictribe.com/media/PLM/data/docs/P0B1X/X-TOUCH_QSG_WW.pdf), p. 24.

2. Download all files in this repository *(Code -> Download ZIP)*. From the ZIP archive, copy all the files in the `fltouch-main` folder to your FL Studio Scripts folder, in a dedicated subfolder. Usually this would be:

- Windows: `%UserProfile%\Documents\Image-Line\Data\FL Studio\Settings\Hardware\fltouch`
- MacOS: `~/Image-Line/FL Studio/Settings/Hardware/fltouch`

3. In FL Studio's MIDI settings *(Options -> Midi settings)*, you'll find your "X-Touch" and "X-Touch-Ext" controllers. Set your X-Touch's MIDI channel to 102 and the extenders to 103, 104, ... and change the controller type to "FLtouch X-Touch" or "FLtouch X-Touch Extender" (depending on if the device is an extender or not).

![FL Studio Midi Settings Screen](https://user-images.githubusercontent.com/3641681/161856471-97810569-0ed5-4123-968a-68a11d295be2.png)

*If these instructions are unclear, you can find a more detailed guide by Zizzer Productions [here](https://www.zizzerproductions.com/post/make-behringer-universal-control-surface-work-with-fl-studio).*

### Layout

![Controller layout](https://user-images.githubusercontent.com/3641681/159065298-c055e292-a587-477a-b0e6-cb76a467cfd9.png)
