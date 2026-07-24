import midi

from behaviors.mcu_base_behavior import McuBaseBehavior
from behaviors.menu_screen_behavior import MenuScreenBehavior
from datatypes.menu_item import MenuItem
from device_hal import mcu_buttons
from device_hal.mcu_device import McuDevice
from utilities.fl_class_import import FlMidiMsg
from utilities.track_banking_manager import TrackBankingManager

class MenuSelectButtonBehavior(McuBaseBehavior):
    """
    Handles SELECT button presses in the Flip menu.

    On press: runs the pressed item's action, then re-renders the menu screen so the new on/off state
    shows immediately. The menu stays open (press Flip to leave); the explicit re-render is needed
    because some actions apply their change without firing an FL OnRefresh, so the screen would
    otherwise keep showing the stale value.
    """

    def __init__(self, mcuDevice: McuDevice, menuBankingManager: TrackBankingManager, menuScreen: MenuScreenBehavior,
                 menuItems: list[MenuItem]):
        super().__init__(mcuDevice)
        self._menuBanking = menuBankingManager
        self._menuScreen = menuScreen
        self._menuItems = menuItems

    def OnMidiMsg(self, event: FlMidiMsg):
        if not (event.midiId == midi.MIDI_NOTEON and event.data2 > 0 and
                mcu_buttons.Select_1 <= event.data1 <= mcu_buttons.Select_8):
            return event

        hardwareIndex = event.data1 - mcu_buttons.Select_1
        virtualIndex = self._menuBanking.GetTrackIndex(hardwareIndex)

        if virtualIndex == -1 or not self._menuBanking.VirtualTrackExists(virtualIndex):
            return event

        self._menuItems[virtualIndex].execute()
        self._menuScreen.RenderScreen() # re-render the menu screen so values are up-to-date

        event.handled = True
        return event
