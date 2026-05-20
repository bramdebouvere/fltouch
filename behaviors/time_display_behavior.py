import device
import midi
import playlist
import ui
import utils

from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal import mcu_buttons
from device_hal.mcu_device import McuDevice

class TimeDisplayBehavior(McuBaseBehavior):
    """ Behavior for updating the time display screen (main unit)"""

    def __init__(self, device: McuDevice):
        super().__init__(device)

    def OnIdle(self):
        self.UpdateTimeDisplay()

    def OnWaitingForInput(self):
        self.McuDevice.TimeDisplay.SetMessage('..........')

    def OnDisable(self):
        # clear time message
        self.McuDevice.TimeDisplay.SetMessage('')

    def UpdateTimeDisplay(self):
        """ Updates the time display to the current value """
        if (not device.isAssigned()):
            return
        
        # time display
        if ui.getTimeDispMin():
            # HHH.MM.SS.CC_
            if playlist.getVisTimeBar() == -midi.MaxInt:
                s = '-   0'
            else:
                n = abs(playlist.getVisTimeBar())
                h, m = utils.DivModU(n, 60)
                s = utils.Zeros_Strict((h * 100 + m) * utils.SignOf(playlist.getVisTimeBar()), 5, ' ') #todo sign of...

            s = s + utils.Zeros_Strict(abs(playlist.getVisTimeStep()), 2) + utils.Zeros_Strict(playlist.getVisTimeTick(), 2) + ' '
        else:
            # BBB.BB.__.TTT
            s = utils.Zeros_Strict(playlist.getVisTimeBar(), 3, ' ') + utils.Zeros_Strict(abs(playlist.getVisTimeStep()), 2) + '  ' + utils.Zeros_Strict(playlist.getVisTimeTick(), 3)

        self.McuDevice.TimeDisplay.SetMessage(s, skipIsAssignedCheck = True)

    def OnRefresh(self, flags):
        super().OnRefresh(flags)

        # LEDs
        if flags & midi.HW_Dirty_LEDs:
            self.UpdateLeds()

    def UpdateLeds(self):
        # SMPTE/BEATS
        isTimeDisp = ui.getTimeDispMin()
        self.McuDevice.SetButton(mcu_buttons.Smpte_Led, midi.TranzPort_OffOnT[isTimeDisp], 3, skipIsAssignedCheck=True)
        self.McuDevice.SetButton(mcu_buttons.Beats_Led, midi.TranzPort_OffOnT[not isTimeDisp], 4, skipIsAssignedCheck=True)
    
