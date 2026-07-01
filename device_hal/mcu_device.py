import device
import midi
import utils

from device_hal import mcu_buttons
from device_hal.mcu_device_track import McuDeviceTrack
from device_hal.mcu_device_time_display import McuDeviceTimeDisplay
from device_hal.mcu_colors import GetMcuColor

class McuDevice:
    """
    Class for controlling the Xtouch in MCU mode (Hardware abstraction)
    """ 

    def __init__(self, isExtender: bool):
        self.isExtender = isExtender
        self.__productId = 0x15 if isExtender else 0x14 # productID used by MCU protocol

        # cache values
        self.__lastScreenColors = [0,0,0,0,0,0,0,0]
        self.__lastTextDisplay = [None, None]

        # create tracks
        self._tracks = [McuDeviceTrack(i, self.__productId, i == 8) for i in range(8 if isExtender else 9)]

        if not isExtender:
            self.TimeDisplay = McuDeviceTimeDisplay()

    def Initialize(self):
        """ Initializes the MCU device """
        self.__lastTextDisplay = [None, None]
        self.__lastScreenColors = [0,0,0,0,0,0,0,0]
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
        self.SendMidiToExtender(extenderIndex, midi.MIDI_NOTEON + (mcu_buttons.SetFirstTrackOnExtender << 8) + (firstTrack << 16))

    def SendButtonPressToExtenders(self, button):
        """ Dispatches a MIDI message to all extenders, letting them know that a button was pressed """
        if self.isExtender:
            return
        self.SendMidiToExtenders(midi.MIDI_NOTEON + (button << 8) + (1 << 16))

    def SendSubModeSwitchToExtender(self, key: int, data:int|None = None):
        """
        Dispatch a sub-mode switch to all dispatch receivers (for McuCompositeMode).
        On the main unit the receivers are the extenders; on an extender the (single) receiver is the main unit.
        key selects the target sub-mode (2 bits, 0-3); data is an optional value (5 bits, 0-31) carried with the switch.
        """
        payload = (key << 5) | (data & 0x1F if data is not None else 0)
        message = midi.MIDI_NOTEON + (mcu_buttons.SubModeSwitch << 8) + (payload << 16)
        receiverCount = device.dispatchReceiverCount()
        for n in range(0, receiverCount):
            device.dispatch(n, message)

    def SetBackLightTimeout(self, Minutes): 
        """ Sets the backlight timeout (0 should switch off immediately, but doesn't really work well) """
        # This is code from the original script, but I don't think it does anything on the Xtouch, might do some stuff on other MCU devices though, so I'm leaving it in for now
        if device.isAssigned():
            device.midiOutSysex(bytes([0xF0, 0x00, 0x00, 0x66, self.__productId, 0x0B, Minutes, 0xF7]))

    def SetClicking(self, enabled: bool):
        """ Sets clicking for transport buttons """
        # According to https://support.apple.com/en-ng/guide/logicpro/ctls718de3eb/mac ,
        # Enabling or disabling clicking turns on or off the audible click sound when you press one of the transport buttons.
        # However, in practice this doesn't seem to do anything on the Xtouch, but it might do something on other MCU devices, so I'm leaving it in for now
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
                assert track.meter is not None
                track.meter.SetValue(0, True)

    def GetTrack(self, index):
        """ Returns the an MCU mixer track instance """
        return self.tracks[index]

    def SetTextDisplay(self, message, row:int = 0, skipIsAssignedCheck: bool = False):
        """ Sends a message to the screen (row 0 = bottom, row 1 = top) """
        if not (skipIsAssignedCheck or device.isAssigned()):
            return
        
        # Cache the last message sent to avoid sending the same message multiple times
        if message == self.__lastTextDisplay[row]:
            return
        self.__lastTextDisplay[row] = message

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
                sysex.append(GetMcuColor(color))
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
        """Send a button LED update.

        For normal button LEDs, `active` is typically one of the
        midi.TranzPort_OffOnT values.
        For low-level note-on style LEDs (like the play sync indicator),
        `active` may include `midi.MIDI_NOTEON` plus a velocity in the high bits.
        """
        if skipIsAssignedCheck or device.isAssigned():
            device.midiOutNewMsg((button << 8) + active, index)

    def __SetMetersActive(self, active: bool, skipIsAssignedCheck: bool = False):
        """ Enables or disables all meters """
        if skipIsAssignedCheck or device.isAssigned():
            for track in self.tracksWithMeters:
                if track.meter is not None:
                    track.meter.SetActive(active, True)

    @property
    def tracks(self):
        """ Returns all track instances belonging to this MCU device """
        return self._tracks

    @property
    def tracksWithMeters(self):
        """ Returns all track instances with meters belonging to this MCU device """
        return [track for track in self.tracks if not track.meter is None]
