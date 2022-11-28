import device
import midi

import mcu_device_fader_conversion

class McuDeviceTrackFader:
    """ Class for controlling a single fader on the Xtouch in MCU mode (Hardware abstraction) """

    def __init__(self, productId: int, index: int, isMain: bool, baseMidiValue: int):
        self.__productId = productId
        self.__index = index
        self.__isMain = isMain
        self.__baseMidiValue = baseMidiValue

    def SetLevelFromFlsFader(self, flFaderValue: int, skipIsAssignedCheck: bool = False):
        """ Sets the value of the fader on the Xtouch using a FL Studio Fader value """
        paramValue = mcu_device_fader_conversion.FlFaderToMcuFader(flFaderValue)
        self.SetLevel(paramValue, skipIsAssignedCheck)

    def SetLevel(self, flParameterValue: int, skipIsAssignedCheck: bool = False):
        """ Sets the value of the fader on the Xtouch (0 to 16380) """
        if skipIsAssignedCheck or device.isAssigned():
            data1 = flParameterValue
            data2 = data1 & 127
            data1 = data1 >> 7
            device.midiOutNewMsg(midi.MIDI_PITCHBEND + self.__index + (data2 << 8) + (data1 << 16), self.__baseMidiValue + 5)
