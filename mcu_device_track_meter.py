import device
import midi

class McuDeviceTrackMeter:
    """ Class for controlling a single track on the Xtouch in MCU mode (Hardware abstraction) """

    def __init__(self, productId: int, trackIndex: int):
        self.__trackIndex = trackIndex
        self.__productId = productId

    def SetActive(self, active: bool, skipIsAssignedCheck: bool = False):
        """ Enables or disables the current meter """
        if skipIsAssignedCheck or device.isAssigned():
            device.midiOutSysex(bytes([0xF0, 0x00, 0x00, 0x66, self.__productId, 0x20, self.__trackIndex, 3 if active else 0, 0xF7]))

    def SetValue(self, value: float, skipIsAssignedCheck: bool = False):
        """ Sets a specific meter to a certain value (0 = off, 1 = max, >1 = clipping) """
        if skipIsAssignedCheck or device.isAssigned():
            meter_value = self.__ConvertToMeterValue(value)
            device.midiOutMsg(midi.MIDI_CHANAFTERTOUCH + (meter_value << 8) + (self.__trackIndex << 12))

    def __ConvertToMeterValue(self, value: float):
        """ Converts an FL Studio meter float value to an MCU compatible value (one char hex) """
        
        # The Xtouch accepts a value from 0-14, 15 being off, so convert the value from float to this
        meter_max = 14
        meter_value = int(value * meter_max)

        # If there's any activity, make sure the meter shows it
        if (value > 0.001 and meter_value == 0):
            meter_value = 1

        # If there's no activity, clear the meter (15)
        if value == 0:
            meter_value = 15

        return meter_value
