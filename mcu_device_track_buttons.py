import device
import midi

import mcu_buttons

class McuDeviceTrackButtons:
    """ Class for controlling track buttons on the Xtouch in MCU mode (Hardware abstraction) """

    def __init__(self, productId: int, trackIndex: int, baseMidiValue: int):
        self.__trackIndex = trackIndex
        self.__productId = productId
        self.__baseMidiValue = baseMidiValue

    def SetArmButton(self, isArmed: bool, isRecording: bool, skipIsAssignedCheck: bool = False):
        """ Sets the Arm button on a track """
        if skipIsAssignedCheck or device.isAssigned():
            device.midiOutNewMsg(((mcu_buttons.Record_1 + self.__trackIndex) << 8) + midi.TranzPort_OffOnBlinkT[int(isArmed) * (1 + int(isRecording))], self.__baseMidiValue + 1)
            
    def SetSoloButton(self, isSolo: bool, skipIsAssignedCheck: bool = False):
        """ Sets the Solo button on a track """
        if skipIsAssignedCheck or device.isAssigned():
            device.midiOutNewMsg(((mcu_buttons.Solo_1 + self.__trackIndex) << 8) + midi.TranzPort_OffOnT[isSolo], self.__baseMidiValue + 2)

    def SetMuteButton(self, isMuted: bool, skipIsAssignedCheck: bool = False):
        """ Sets the Mute button on a track """
        if skipIsAssignedCheck or device.isAssigned():
            device.midiOutNewMsg(((mcu_buttons.Mute_1 + self.__trackIndex) << 8) + midi.TranzPort_OffOnT[isMuted], self.__baseMidiValue + 3)

    def SetSelectButton(self, isSelected: bool, skipIsAssignedCheck: bool = False):
        """ Sets the Select button on a track """
        if skipIsAssignedCheck or device.isAssigned():
            device.midiOutNewMsg(((mcu_buttons.Select_1 + self.__trackIndex) << 8) + midi.TranzPort_OffOnT[isSelected], self.__baseMidiValue + 4)

    def SetButtonByIndex(self, index: int, active: bool, skipIsAssignedCheck: bool = False):
        """ Take a button by its index (0 = Arm, 1 = Solo, 2 = Mute, 3 = Select) and turn it on or off """
        if skipIsAssignedCheck or device.isAssigned():
            device.midiOutNewMsg(((index * 8 + self.__trackIndex) << 8) + midi.TranzPort_OffOnT[active], self.__baseMidiValue + 1 + index)
