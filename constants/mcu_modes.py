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

# 2-char labels shown on the main unit's assignment display, per mode
ModeAssignmentLabels = {
    mcu_buttons.Pan:       'Pn',
    mcu_buttons.Stereo:    'St',
    mcu_buttons.Sends:     'SE',
    mcu_buttons.Equalizer: 'Eq',
    mcu_buttons.Effects:   'Ef',
    mcu_buttons.Free:      'Ch',
}
