import midi

from modes.mcu_composite_mode import McuCompositeMode
from utilities import channel_rack_mode_state
from utilities.fl_class_import import FlMidiMsg
from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal.mcu_device import McuDevice
from device_hal import mcu_buttons

class ChannelParamSelectButtonBehavior(McuBaseBehavior):
    """
    Handles SELECT buttons and their LEDs while the Channel Rack parameter view is active.

    On enable: lights every SELECT LED as a visual cue that pressing SELECT returns to the channel overview.
    On disable: clears the LEDs.
    On SELECT press: requests a switch back to the channel overview.
    """

    def __init__(self, mcuDevice: McuDevice, compositeMode: McuCompositeMode):
        super().__init__(mcuDevice)
        self._compositeMode = compositeMode

    def OnEnable(self):
        super().OnEnable()
        self.__setAllSelectLeds(True)

    def OnDisable(self):
        self.__setAllSelectLeds(False)
        super().OnDisable()

    def OnMidiMsg(self, event: FlMidiMsg):
        if (event.midiId == midi.MIDI_NOTEON and event.data2 > 0 and
                mcu_buttons.Select_1 <= event.data1 <= mcu_buttons.Select_8):
            self._compositeMode.SwitchTo(channel_rack_mode_state.OVERVIEW)
            event.handled = True
        return event

    def __setAllSelectLeds(self, on: bool):
        for track in self.McuDevice.tracksWithMeters:
            if track.buttons is not None:
                track.buttons.SetSelectButton(on)
