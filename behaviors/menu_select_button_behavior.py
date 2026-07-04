import midi
import mixer

from behaviors.mcu_base_behavior import McuBaseBehavior
from constants import menu_items
from device_hal import mcu_buttons
from device_hal.mcu_device import McuDevice
from modes.mcu_composite_mode import McuCompositeMode
from utilities import mixer_menu_state
from utilities.fl_class_import import FlMidiMsg
from utilities.track_banking_manager import TrackBankingManager

class MenuSelectButtonBehavior(McuBaseBehavior):
    """
    Handles SELECT button presses in the Flip menu.

    On press: runs the pressed item's action against the currently selected mixer track, then returns
    to the overview sub-mode.
    """

    def __init__(self, mcuDevice: McuDevice, menuBankingManager: TrackBankingManager, compositeMode: McuCompositeMode):
        super().__init__(mcuDevice)
        self._menuBanking = menuBankingManager
        self._compositeMode = compositeMode

    def OnMidiMsg(self, event: FlMidiMsg):
        if not (event.midiId == midi.MIDI_NOTEON and event.data2 > 0 and
                mcu_buttons.Select_1 <= event.data1 <= mcu_buttons.Select_8):
            return event

        hardwareIndex = event.data1 - mcu_buttons.Select_1
        virtualIndex = self._menuBanking.GetTrackIndex(hardwareIndex)

        if virtualIndex == -1 or not self._menuBanking.VirtualTrackExists(virtualIndex):
            return event

        menu_items.ExecuteMenuItem(virtualIndex, mixer.trackNumber())
        self._compositeMode.SwitchTo(mixer_menu_state.OVERVIEW)

        event.handled = True
        return event
