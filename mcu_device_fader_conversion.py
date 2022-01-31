# For conversions between FL studio's mixer fader level and the MCU's fader level

import midi

McuSliderMax = round(13072 * 16000 / 12800)

def FlFaderToMcuFader(Value, Max = midi.FromMIDI_Max):
    """ Convert FL Studio mixer track fader level to Behringer Xtouch slider level """
    return round(Value / Max * McuSliderMax)

def McuFaderToFlFader(Value, Max = midi.FromMIDI_Max):
    """ Convert Behringer Xtouch slider level to FL Studio mixer track fader level"""
    return min(round(Value / McuSliderMax * Max), Max)
