import device
import midi

from device_hal import mcu_knob_mode

class McuDeviceTrackEncoderKnob:
    """ Class for controlling the encoder knob on the Xtouch in MCU mode (Hardware abstraction) """

    def __init__(self, trackIndex: int, baseMidiValue: int):
        self.__trackIndex = trackIndex
        self.__baseMidiValue = baseMidiValue

        # Cache values
        self.__lastKnobMode = -1
        self.__lastShowCenter = None
        self.__lastValue = -1

    def SetLedsValue(self, knobMode: int, showCenter: bool, value: int):
        """
        Sets a value (0-11) and a knob mode on the rotary encoder
        See https://drive.google.com/file/d/1Tn85UbcrIjd7vpjRnOx9p6jgWucofnh3/view , page 112, for more info about the knob modes
        showCenter: True = center led on, False = center led off
        value: 0 = all leds in ring off, 1-5 = left side leds, 6 = center led, 7-11 = right side leds
        """
        
        # Cache values, so we don't send the same message multiple times
        if knobMode == self.__lastKnobMode and showCenter == self.__lastShowCenter and value == self.__lastValue:
            return
        self.__lastKnobMode = knobMode
        self.__lastShowCenter = showCenter
        self.__lastValue = value

        trackBits = 0x30 + self.__trackIndex

        centerBits = int(showCenter) << 6
        modeBits = knobMode << 4
        dataBits = centerBits + modeBits + value

        device.midiOutNewMsg(midi.MIDI_CONTROLCHANGE + (trackBits << 8) + (dataBits << 16), self.__baseMidiValue)
    
    def SetLedsValueNone(self):
        """
        All LEDs on the rotary encoder OFF
        """
        self.SetLedsValue(mcu_knob_mode.SingleDot, False, 0)

    def SetLedsValueAll(self):
        """
        All LEDs on the rotary encoder ON
        """
        self.SetLedsValue(mcu_knob_mode.Wrap, True, 11)
