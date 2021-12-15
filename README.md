# fltouch
FL Studio MIDI scripts for the Behringer X-Touch + extender(s) (Mackie Control Universal) MIDI controllers, based on the official scripts by Image-Line.

## Differences with the official scripts
- Support for multiple extenders
- Improved knob resolution and acceleration
- Forces jog dial to use the playlist instead changing the active mixer channel
- Auto channel selection when touching a fader
- Minor bugfixes

## How to use
Put [device_MackieCU.py](./device_MackieCU.py) and [device_MackieCU_Ext.py](./device_MackieCU.py) in your FL Studio Scripts folder (usually this would be `<Documents>\Image-Line\Data\FL Studio\Settings\Hardware\Mackie Control Unit`).

In FL Studio's MIDI settings, set your X-Touch's MIDI channel to 102 and extenders to 103, 104, ...