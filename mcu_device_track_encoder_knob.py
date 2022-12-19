import device
import midi

import mcu_knob_mode

class McuDeviceTrackEncoderKnob:
    """ Class for controlling the encoder knob on the Xtouch in MCU mode (Hardware abstraction) """

    def __init__(self, trackIndex: int, baseMidiValue: int):
        self.__trackIndex = trackIndex
        self.__baseMidiValue = baseMidiValue

    def setLedsValue(self, knobMode: int, showCenter: bool, value: int):
        """
        Sets a value (0-11) and a knob mode on the rotary encoder 
        See https://drive.google.com/file/d/1Tn85UbcrIjd7vpjRnOx9p6jgWucofnh3/view , page 112, for more info about the knob modes
        """

        trackBits = 0x30 + self.__trackIndex

        centerBits = int(showCenter) << 6
        modeBits = knobMode << 4
        dataBits = centerBits + modeBits + value

        device.midiOutNewMsg(midi.MIDI_CONTROLCHANGE + (trackBits << 8) + (dataBits << 16), self.__baseMidiValue)
    
    def SetLedsValueNone(self):
        """
        All LEDs on the rotary encoder OFF
        """
        self.setLedsValue(mcu_knob_mode.SingleDot, False, 0)

    def setLedsValueAll(self):
        """
        All LEDs on the rotary encoder ON
        """
        self.setLedsValue(mcu_knob_mode.Wrap, True, 11)
