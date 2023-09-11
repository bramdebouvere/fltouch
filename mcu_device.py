import device
import midi
import utils

import mcu_device_track
import mcu_device_time_display
import mcu_colors

class McuDevice:
    """
    Class for controlling the Xtouch in MCU mode (Hardware abstraction)
    """ 

    def __init__(self, isExtender: bool):
        self.isExtender = isExtender
        self.__productId = 0x15 if isExtender else 0x14 # productID used by MCU protocol
        self.__lastScreenColors = [0,0,0,0,0,0,0,0]

        # create tracks
        self._tracks = [mcu_device_track.McuDeviceTrack(i, self.__productId, i == 8) for i in range(8 if isExtender else 9)]

        if not isExtender:
            self.TimeDisplay = mcu_device_time_display.McuDeviceTimeDisplay()


    def Initialize(self):
        """ Initializes the MCU device """
        if device.isAssigned():
            device.midiOutSysex(bytes([0xF0, 0x00, 0x00, 0x66, self.__productId, 0x0C, 1, 0xF7]))

    def SendMidiToExtenders(self, message): 
        """ Dispatches a MIDI message to all receivers (extenders) """
        receiverCount = device.dispatchReceiverCount()
        for n in range(0, receiverCount):
            device.dispatch(n, message)

    def SendMidiToExtender(self, extenderIndex, message):
        """ Dispatches a MIDI message to a specific receiver (extender) """
        receiverCount = device.dispatchReceiverCount()
        if (extenderIndex >= 0 and extenderIndex < receiverCount):
            device.dispatch(extenderIndex, message)

    def SetFirstTrackOnExtender(self, extenderIndex, firstTrack):
        """ Dispatches a MIDI message to an extender to let them know their first track """
        if self.isExtender:
            return
        self.SendMidiToExtender(extenderIndex, midi.MIDI_NOTEON + (0x7F << 8) + (firstTrack << 16))

    def SetBackLightTimeout(self, Minutes): 
        """ Sets the backlight timeout (0 should switch off immediately, but doesn't really work well) """
        # This is code from the original script, but I don't think it does anything on the Xtouch, might do some stuff on other MCU devices though, so I'm leaving it in for now
        if device.isAssigned():
            device.midiOutSysex(bytes([0xF0, 0x00, 0x00, 0x66, self.__productId, 0x0B, Minutes, 0xF7]))

    def SetClicking(self, enabled: bool):
        """ Sets clicking for transport buttons """
        # This is code from the original script, but I don't know what the clicking actually means in this case (if you do, please let me know)
        if device.isAssigned():
            device.midiOutSysex(bytes([0xF0, 0x00, 0x00, 0x66, self.__productId, 0x0A, int(enabled), 0xF7]))

    def EnableMeters(self):
        """ Enables all meters """
        if device.isAssigned():
            # set vertical meter mode (is the one that works properly on XTouch, but other MCU devices also support other ones)
            device.midiOutSysex(bytes([0xF0, 0x00, 0x00, 0x66, self.__productId, 0x21, 1, 0xF7]))
            # enable meters
            self.__SetMetersActive(True, True)

    def DisableMeters(self):
        """ Disables all meters """
        if device.isAssigned():
            self.__SetMetersActive(False, True)

    def ClearMeters(self):
        """ Clear peak indicators """
        if device.isAssigned():
            for track in self.tracksWithMeters:
                track.meter.SetValue(0, True)

    def GetTrack(self, index):
        """ Returns the an MCU mixer track instance """
        return self.tracks[index]

    def SetTextDisplay(self, message, row:int = 0, skipIsAssignedCheck: bool = False):
        """ Sends a message to the screen (row 0 = bottom, row 1 = top) """
        if skipIsAssignedCheck or device.isAssigned():
            lastMsgLen = 0x37
            maxLen = 56 # The screens can only show 56 characters in total

            sysex = bytearray([0xF0, 0x00, 0x00, 0x66, self.__productId, 0x12, (lastMsgLen + 1) * row]) + bytearray(message.ljust(lastMsgLen + 1, ' ')[:maxLen], 'ascii')
            sysex.append(0xF7)
            device.midiOutSysex(bytes(sysex))

    def SetScreenColors(self, colorArray = [-10261391,-10261391,-10261391,-10261391,-10261391,-10261391,-10261391,-10261391], skipIsAssignedCheck: bool = False):
        """ Sets the colors of the screens (all white by default) """
        if len(colorArray) != 8:
            return
        if colorArray == self.__lastScreenColors:
            return
        if skipIsAssignedCheck or device.isAssigned():
            sysex = bytearray([0xF0, 0x00, 0x00, 0x66, self.__productId, 0x72])
            for color in colorArray:
                sysex.append(mcu_colors.GetMcuColor(color))
            sysex.append(0xF7)
            device.midiOutSysex(bytes(sysex))
            self.__lastScreenColors = colorArray

    def SetAssignmentMessage(self, number= -1, skipIsAssignedCheck: bool = False):
        """ Sets the assignment screen (shows track number, -1 = empty) """
        # if -1, show empty, else fill with spaces so it's at least 2 characters
        message = '  ' if number == -1 else utils.Zeros(number, 2, ' ')

        # only show the last 2 characters if the message is longer
        message = message[-2:]

        # send to display
        if skipIsAssignedCheck or device.isAssigned():
            device.midiOutMsg(midi.MIDI_CONTROLCHANGE + ((0x4B) << 8) + (ord(message[0]) << 16))
            device.midiOutMsg(midi.MIDI_CONTROLCHANGE + ((0x4A) << 8) + (ord(message[1]) << 16))

    def SetButton(self, button: int, active: int, index:int, skipIsAssignedCheck: bool = False):
        """ Take a button and turn it on or off """
        if skipIsAssignedCheck or device.isAssigned():
            device.midiOutNewMsg((button << 8) + active, index)

    def __SetMetersActive(self, active: bool, skipIsAssignedCheck: bool = False):
        """ Enables or disables all meters """
        if skipIsAssignedCheck or device.isAssigned():
            for track in self.tracksWithMeters:
                track.meter.SetActive(active, True)

    @property
    def tracks(self):
        """ Returns all track instances belonging to this MCU device """
        return self._tracks

    @property
    def tracksWithMeters(self):
        """ Returns all track instances with meters belonging to this MCU device """
        return [track for track in self.tracks if not track.meter is None]
