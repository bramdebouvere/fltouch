import midi
import mixer

from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal.mcu_device import McuDevice
from device_hal.mcu_device_fader_conversion import McuFaderToFlFader


class MixerMainFaderBehavior(McuBaseBehavior):
    """Behavior for synchronizing the master fader on the main X-Touch unit."""

    def __init__(self, mcuDevice: McuDevice):
        super().__init__(mcuDevice)

    def OnRefresh(self, flags):
        super().OnRefresh(flags)
        if self.McuDevice.isExtender:
            return

        if not (flags & midi.HW_Dirty_Mixer_Controls):
            return

        masterTrack = self.McuDevice.GetTrack(8)
        if masterTrack is not None:
            masterValue = mixer.getEventValue(midi.REC_MainVol)
            masterTrack.fader.SetLevelFromFlsFader(masterValue, False)

    def OnMidiMsg(self, event):
        if self.McuDevice.isExtender:
            return super().OnMidiMsg(event)

        if event.midiId != midi.MIDI_PITCHBEND or event.midiChan != 8:
            return super().OnMidiMsg(event)
        
        event.inEv = event.data1 + (event.data2 << 7)
        event.outEv = (event.inEv << 16) // 16383
        event.inEv -= 0x2000

        flFaderValue = McuFaderToFlFader(event.inEv + 0x2000)
        mixer.automateEvent(midi.REC_MainVol, flFaderValue, midi.REC_MIDIController, 0)

        event.handled = True
        return event

    def OnIdle(self):
        super().OnIdle()
        if self.McuDevice.isExtender:
            return

        masterTrack = self.McuDevice.GetTrack(8)
        if masterTrack is not None:
            masterValue = mixer.getEventValue(midi.REC_MainVol)
            masterTrack.fader.SetLevelFromFlsFader(masterValue, False)
