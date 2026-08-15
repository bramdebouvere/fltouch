import device
import midi

from device_hal.mcu_device_fader_conversion import FlFaderToMcuFader

class McuDeviceTrackFader:
    """ Class for controlling a single fader on the Xtouch in MCU mode (Hardware abstraction) """

    def __init__(self, productId: int, index: int, isMain: bool, baseMidiValue: int):
        self.__productId = productId
        self.__index = index
        self.__isMain = isMain
        self.__baseMidiValue = baseMidiValue
        self.__lastLevel = -1 # store the last set level to avoid sending redundant MIDI messages (-1 means no level has been set yet)

    def SetLevelFromFlsFader(self, flFaderValue: int, skipIsAssignedCheck: bool = False):
        """ Sets the value of the fader on the Xtouch using a FL Studio Fader value """
        paramValue = FlFaderToMcuFader(flFaderValue)
        self.SetLevel(paramValue, skipIsAssignedCheck)
        
    def SetLevel(self, value: int, skipIsAssignedCheck: bool = False):
        """ Sets the value of the fader on the Xtouch (0 to 16380) """

        # If the value hasn't changed, don't send a new MIDI message
        if value == self.__lastLevel:
            return
        self.__lastLevel = value

        # Send the MIDI message
        if skipIsAssignedCheck or device.isAssigned():
            data1 = value
            data2 = data1 & 127
            data1 = data1 >> 7
            device.midiOutNewMsg(midi.MIDI_PITCHBEND + self.__index + (data2 << 8) + (data1 << 16), self.__baseMidiValue + 5)
