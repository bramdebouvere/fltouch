# Mackie CU modes

from device_hal import mcu_buttons


Pan = 0
Stereo = 1
Sends = 2
Equalizer = 3
Effects = 4
Free = 5

ButtonModeMapping = {
    mcu_buttons.Pan: Pan,
    mcu_buttons.Stereo: Stereo,
    mcu_buttons.Sends: Sends,
    mcu_buttons.Equalizer: Equalizer,
    mcu_buttons.Effects: Effects,
    mcu_buttons.Free: Free
}
