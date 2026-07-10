import device
import midi
import transport
import ui

from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal import mcu_buttons
from utilities.button_manager import ButtonManager


class WindowTimeButtonsBehavior(McuBaseBehavior):
    """Handles Browser, StepSequencer, Window, In, Out, Select buttons."""

    def __init__(self, mcuDevice):
        super().__init__(mcuDevice)

    def OnMidiMsg(self, event):
        if event.midiId == midi.MIDI_NOTEON and event.data1 in [
            mcu_buttons.Browser,
            mcu_buttons.Main,
            mcu_buttons.Window,
            mcu_buttons.In,
            mcu_buttons.Out,
            mcu_buttons.Select,
        ]:
            btn = event.data1

            if btn == mcu_buttons.Browser:
                if event.data2 > 0 and event.pmeFlags & midi.PME_System_Safe:
                    ui.showWindow(midi.widBrowser)
                    ui.setFocused(midi.widBrowser)
                self.McuDevice.SetButton(
                    mcu_buttons.Browser,
                    midi.TranzPort_OffOnT[ui.getFocused(midi.widBrowser)],
                    20
                )

            elif btn == mcu_buttons.Main:
                if event.data2 > 0 and event.pmeFlags & midi.PME_System_Safe:
                    # does not always seem to work, I think it's a bug in FL Studio.
                    # I reported it here: https://forum.image-line.com/viewtopic.php?p=2061850#p2061850
                    ui.showWindow(midi.widPlaylist)
                    ui.setFocused(midi.widPlaylist)
                self.McuDevice.SetButton(
                    mcu_buttons.Main,
                    midi.TranzPort_OffOnT[ui.getFocused(midi.widPlaylist)],
                    21
                )

            elif btn == mcu_buttons.Window:
                # Window acts as a jog source
                if event.data2 == 0:
                    if ButtonManager.JogSource == btn:
                        ButtonManager.JogSource = 0
                else:
                    if ButtonManager.JogSource == 0:
                        ButtonManager.JogSource = btn
                device.directFeedback(event)

            elif btn in [mcu_buttons.In, mcu_buttons.Out, mcu_buttons.Select]:
                if btn == mcu_buttons.Select:
                    n = midi.FPT_Punch
                else:
                    n = midi.FPT_PunchIn + btn - mcu_buttons.In

                # Don't send directFeedback on release of the In button, it stays on until Out is pressed.
                if not (btn == mcu_buttons.In and event.data2 == 0):
                    device.directFeedback(event)

                # When Out is pressed or Select fires, turn off the In LED so it
                # doesn't stay lit while Out/Select is active.
                if btn >= mcu_buttons.Out and event.data2 >= int(btn == mcu_buttons.Out):
                    if device.isAssigned():
                        device.midiOutMsg((mcu_buttons.In << 8) + midi.TranzPort_OffOnT[False])

                transport.globalTransport(n, int(event.data2 > 0) * 2, event.pmeFlags)

            event.handled = True
            return event

        return super().OnMidiMsg(event)

    def OnRefresh(self, flags):
        if flags & midi.HW_Dirty_LEDs or flags & midi.HW_Dirty_FocusedWindow:
            self.McuDevice.SetButton(
                mcu_buttons.Browser,
                midi.TranzPort_OffOnT[ui.getFocused(midi.widBrowser)],
                20
            )
            self.McuDevice.SetButton(
                mcu_buttons.Main,
                midi.TranzPort_OffOnT[ui.getFocused(midi.widPlaylist)],
                21
            )
        super().OnRefresh(flags)
