import device
import midi

class McuDeviceTimeDisplay:
    def __init__(self):
        self.__lastTimeMsg = bytearray(10)

    def SetMessage(self, message, skipIsAssignedCheck = False):
        """ Sets the message on the time display """
        TimeMsg = bytearray(10)
        for n in range(0, len(message)):
            TimeMsg[n] = ord(message[n])

        if skipIsAssignedCheck or device.isAssigned():
            #send chars that have changed
            for m in range(0, min(len(self.__lastTimeMsg), len(TimeMsg))):
                if self.__lastTimeMsg[m] != TimeMsg[m]:
                    device.midiOutMsg(midi.MIDI_CONTROLCHANGE + ((0x49 - m) << 8) + ((TimeMsg[m]) << 16))

        self.__lastTimeMsg = TimeMsg
