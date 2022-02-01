# fltouch
FL Studio MIDI scripts for the Behringer X-Touch + extender(s) (Mackie Control Universal) MIDI controllers, based on the official scripts by Image-Line.

## Differences with the official scripts
- Support for multiple extenders
- Improved knob resolution and acceleration
- Improved jog wheel with automatic window focus
- Auto channel selection when touching a fader
- Make use of the full scribble strip width
- Meter values are more accurate
- The clip led works when the signal is clipping
- Smoothing is disabled by default
- Sliders now function in free control mode
- Changing the tempo using the jog wheel now works
- Various bugfixes and improvements

More improvements later...

## How to use

### Installation

1. This script uses the Mackie Control Universal (MCU) protocol. Your X-Touch and the extenders will need to be set to MCU mode. To do so, check out "*Step 3: Getting started*" in [the official quick-start guide](https://mediadl.musictribe.com/media/PLM/data/docs/P0B1X/X-TOUCH_QSG_WW.pdf).

2. Download all files in this repository *(Code -> Download ZIP)*. From the ZIP archive, copy all the files in the `fltouch-main` folder to your FL Studio Scripts folder, in a dedicated subfolder (usually this would be `%UserProfile%\Documents\Image-Line\Data\FL Studio\Settings\Hardware\fltouch`).

3. In FL Studio's MIDI settings *(Options -> Midi settings)*, you'll find your "X-Touch" and "X-Touch-Ext" controllers. Set your X-Touch's MIDI channel to 102 and the extenders to 103, 104, ... and change the controller type to "FLtouch X-Touch" or "FLtouch X-Touch Extender" (depending on if the device is an extender or not). 
![FL Studio Midi Settings Screen](https://user-images.githubusercontent.com/3641681/146776383-881f86f8-23a2-447d-92a4-8486697f1908.png)

### Layout
![Controller layout](https://user-images.githubusercontent.com/3641681/146751933-f87b5be7-c3c2-41ce-8025-19574a23abfa.png)
