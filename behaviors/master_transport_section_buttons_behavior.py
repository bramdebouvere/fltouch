import device
import midi
import transport
import ui
import general
import mixer

from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal import mcu_buttons
from device_hal.mcu_device import McuDevice
from utilities.button_manager import ButtonManager

class MasterTransportSectionButtonsBehavior(McuBaseBehavior):
    """Behavior for master transport section buttons such as shift."""

    def __init__(self, mcuDevice: McuDevice):
        super().__init__(mcuDevice)
        self.Clicking = False

    def OnMidiMsg(self, event):
        if event.midiId != midi.MIDI_NOTEON:
            return super().OnMidiMsg(event)

        if event.data1 == mcu_buttons.Shift:
            ButtonManager.ShiftPressed = event.data2 > 0
            device.directFeedback(event)
            event.handled = True
            return event

        elif event.data1 == mcu_buttons.Edison:
            device.directFeedback(event) #feedback first, because launching edison can cause a delay
            if event.data2 > 0:
                ui.launchAudioEditor(False, '', mixer.trackNumber(), 'AudioLoggerTrack.fst', '')
            event.handled = True
            return event

        elif event.data1 == mcu_buttons.Metronome:
            if event.data2 > 0:
                if ButtonManager.ShiftPressed:
                    self.Clicking = not self.Clicking
                    self.McuDevice.SetClicking(self.Clicking)
                else:
                    transport.globalTransport(midi.FPT_Metronome, 1, event.pmeFlags)
            event.handled = True
            return event

        elif event.data1 == mcu_buttons.CountDown:
            if event.data2 > 0:
                transport.globalTransport(midi.FPT_CountDown, 1, event.pmeFlags)
            event.handled = True
            return event

        elif event.data1 == mcu_buttons.SongVSLoop:
            transport.globalTransport(midi.FPT_Loop, int(event.data2 > 0) * 2, event.pmeFlags)
            event.handled = True
            return event

        elif event.data1 == mcu_buttons.Mode:
            # TODO: this is kind of stupid, because it does the same as the record button below it
            # let's find another feature to map to this button
            transport.globalTransport(midi.FPT_Mode, int(event.data2 > 0) * 2, event.pmeFlags)
            device.directFeedback(event)
            event.handled = True
            return event

        elif event.data1 == mcu_buttons.Snap:
            if ButtonManager.ShiftPressed:
                if event.data2 > 0:
                    transport.globalTransport(midi.FPT_SnapMode, 1, event.pmeFlags)
            else:
                transport.globalTransport(midi.FPT_Snap, int(event.data2 > 0) * 2, event.pmeFlags)
            event.handled = True
            return event

        return super().OnMidiMsg(event)

    def OnRefresh(self, flags):
        if flags & midi.HW_Dirty_LEDs and device.isAssigned():
            self.McuDevice.SetButton(
                mcu_buttons.SongVSLoop,
                midi.TranzPort_OffOnT[transport.getLoopMode() == midi.SM_Pat],
                1
            )
            self.McuDevice.SetButton(
                mcu_buttons.Metronome,
                midi.TranzPort_OffOnT[general.getUseMetronome()],
                12
            )
            self.McuDevice.SetButton(
                mcu_buttons.CountDown,
                midi.TranzPort_OffOnT[general.getPrecount()],
                13
            )
            self.McuDevice.SetButton(
                mcu_buttons.Snap,
                midi.TranzPort_OffOnT[ui.getSnapMode() != 3],
                19
            )
        super().OnRefresh(flags)
