import midi
import mixer

from modes.mcu_composite_mode import McuCompositeMode
from utilities.fl_class_import import FlMidiMsg
from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal.mcu_device import McuDevice
from device_hal import mcu_buttons
from utilities.track_banking_manager import TrackBankingManager
from utilities.effects_mode_state import PARAMS

class EffectsSlotSelectButtonBehavior(McuBaseBehavior):
    """
    Handles SELECT button presses in the effects slot overview.

    On press: validates the targeted slot, opens the plugin window (on the unit with system-safe
    context), and requests a switch to the parameter view for that slot.
    """

    def __init__(self, mcuDevice: McuDevice, slotBankingManager: TrackBankingManager, compositeMode: McuCompositeMode):
        super().__init__(mcuDevice)
        self._slotBankingManager = slotBankingManager
        self._compositeMode = compositeMode

    def OnMidiMsg(self, event: FlMidiMsg):
        if not (event.midiId == midi.MIDI_NOTEON and event.data2 > 0 and
                mcu_buttons.Select_1 <= event.data1 <= mcu_buttons.Select_8):
            return event

        # Get the current mixer track and the slot that for the pressed button
        hardwareIndex = event.data1 - mcu_buttons.Select_1
        slot = self._slotBankingManager.GetTrackIndex(hardwareIndex)
        track = mixer.trackNumber()

        # Check if a plugin exists in the selected slot
        if (slot == -1 or not self._slotBankingManager.VirtualTrackExists(slot) or
                not mixer.isTrackPluginValid(track, slot)):
            return event

        # Open the plugin window
        if event.pmeFlags & midi.PME_System_Safe:
            mixer.focusEditor(track, slot)

        # Switch to the effects parameter view
        self._compositeMode.SwitchTo(PARAMS, slot)

        event.handled = True
        return event
