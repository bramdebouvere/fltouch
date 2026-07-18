import midi

from utilities.fl_class_import import FlMidiMsg

from behaviors.mcu_base_behavior import McuBaseBehavior
from utilities.track_banking_manager import TrackBankingManager
from device_hal import mcu_buttons
from device_hal.mcu_device import McuDevice

class TrackBankingBehavior(McuBaseBehavior):
    """Behavior for handling track banking button presses."""
    def __init__(self, mcuDevice: McuDevice, trackBankingManager: TrackBankingManager):
        super().__init__(mcuDevice)
        self._trackBankingManager = trackBankingManager

    def OnEnable(self):
        super().OnEnable()

    def OnDisable(self):
        super().OnDisable()

    def OnMidiMsg(self, event: FlMidiMsg):
        # Handle bank buttons
        if event.midiId == midi.MIDI_NOTEON and event.data2 > 0:
            if event.data1 in [mcu_buttons.FaderBankLeft, mcu_buttons.FaderBankRight, mcu_buttons.FaderChannelLeft, mcu_buttons.FaderChannelRight]:
                self._trackBankingManager.HandleBankButton(event.data1)
                event.handled = True
                return
        # Handle track banking from main unit to extender
        if event.midiId == midi.MIDI_NOTEON and event.data1 == mcu_buttons.SetFirstTrackOnExtender:
            self._trackBankingManager.SetFirstTrackIndex(event.data2)
            event.handled = True
            return
        return super().OnMidiMsg(event)


