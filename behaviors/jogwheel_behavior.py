import device
import midi
import transport
import ui
import general
import mixer
import channels
import patterns
from behaviors.mcu_base_screen_behavior import McuBaseScreenBehavior
import constants.mcu_constants as mcu_constants
import utilities.transliteration as transliteration

from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal import mcu_buttons
from device_hal.mcu_device import McuDevice
from utilities.button_manager import ButtonManager


class JogWheelBehavior(McuBaseBehavior):
    """Behavior for the jog wheel, jog sources and scrub mode."""

    def __init__(self, mcuDevice: McuDevice, screenBehavior: McuBaseScreenBehavior):
        super().__init__(mcuDevice)
        self._scrub = False
        self._screenBehavior = screenBehavior

    def OnMidiMsg(self, event):
        # Handle jog wheel rotation as a control change on the jog controller.
        if event.midiId == midi.MIDI_CONTROLCHANGE and event.midiChan == 0 and event.data1 == mcu_constants.JogCC:
            event.inEv = event.data2
            if event.inEv >= 0x40:
                event.outEv = -(event.inEv - 0x40)
            else:
                event.outEv = event.inEv

            self.Jog(event)
            event.handled = True
            return event
        
        # Handle toggle and source buttons.
        if event.midiId == midi.MIDI_NOTEON:
            if event.data1 == mcu_buttons.Scrub:
                if event.data2 > 0:
                    self._scrub = not self._scrub
                self.McuDevice.SetButton(mcu_buttons.Scrub, midi.TranzPort_OffOnT[self._scrub], 15)
                event.handled = True
                return event
        
        return super().OnMidiMsg(event)

    def OnRefresh(self, flags):
        if flags & midi.HW_Dirty_LEDs and device.isAssigned():
            self.McuDevice.SetButton(mcu_buttons.Scrub, midi.TranzPort_OffOnT[self._scrub], 15)
        super().OnRefresh(flags)

    def TrackSel(self, Index, Step):
        Index = 2 - Index
        if Index == 0:  # Channel Rack channel
            if 0 <= channels.channelNumber() + Step < channels.channelCount():
                device.baseTrackSelect(Index, Step)
            channelNumber = channels.channelNumber()
            if 0 <= channelNumber < channels.channelCount():
                s = channels.getChannelName(channelNumber)
            else:
                s = 'No channel selected'
            self._screenBehavior.OnSendTempMsg(mcu_constants.ArrowsStr + 'Channel: ' + s)
        elif Index == 1:  # Mixer track
            if 0 <= mixer.trackNumber() + Step < (mixer.trackCount() -1):
                device.baseTrackSelect(Index, Step)
            self._screenBehavior.OnSendTempMsg(mcu_constants.ArrowsStr + 'Mixer track: ' + transliteration.GetAsciiSafeTrackName(mixer.trackNumber()))
        elif Index == 2:  # Pattern
            device.baseTrackSelect(Index, Step)
            s = patterns.getPatternName(patterns.patternNumber())
            self._screenBehavior.OnSendTempMsg(mcu_constants.ArrowsStr + 'Pattern: ' + s)

    def SetJogSource(self, Value):
        ButtonManager.JogSource = Value

    def Jog(self, event):

        jogsrc = ButtonManager.JogSource
        if jogsrc == 0:
            if ui.getFocused(midi.widBrowser):
                transport.globalTransport(midi.FPT_Jog, event.outEv, event.pmeFlags)
            else:
                ui.showWindow(midi.widPlaylist)
                ui.setFocused(midi.widPlaylist)
                if self._scrub:
                    oldSongPos = transport.getSongPos(midi.SONGLENGTH_ABSTICKS)
                    transport.setSongPos(oldSongPos + event.outEv * (1 + 9 * (not ButtonManager.ShiftPressed)), midi.SONGLENGTH_ABSTICKS)
                else:
                    transport.globalTransport(midi.FPT_Jog, event.outEv, event.pmeFlags)
        elif jogsrc == mcu_buttons.Move:
            transport.globalTransport(midi.FPT_MoveJog, event.outEv, event.pmeFlags)
        elif jogsrc == mcu_buttons.Marker:
            ui.showWindow(midi.widPlaylist)
            ui.setFocused(midi.widPlaylist)
            s = 'Marker selection' if ButtonManager.ShiftPressed else 'Marker jump'
            if event.outEv != 0 and transport.globalTransport(midi.FPT_MarkerJumpJog + int(ButtonManager.ShiftPressed), event.outEv, event.pmeFlags) == midi.GT_Global:
                s = ui.getHintMsg()
            self._screenBehavior.OnSendTempMsg(mcu_constants.ArrowsStr + s)
        elif jogsrc == mcu_buttons.Undo:
            s = 'Undo history' if event.outEv == 0 else 'Undo history'
            if event.outEv != 0 and transport.globalTransport(midi.FPT_UndoJog, event.outEv, event.pmeFlags) == midi.GT_Global:
                s = ui.getHintMsg()
            self._screenBehavior.OnSendTempMsg(mcu_constants.ArrowsStr + s + ' (level ' + general.getUndoLevelHint() + ')')
        elif jogsrc == mcu_buttons.Zoom:
            if event.outEv != 0:
                transport.globalTransport(midi.FPT_HZoomJog + int(ButtonManager.ShiftPressed), event.outEv, event.pmeFlags)
        elif jogsrc == mcu_buttons.Window:
            print('window jog' + str(event.outEv))
            if event.outEv != 0:
                transport.globalTransport(midi.FPT_WindowJog, event.outEv, event.pmeFlags)
            s = ui.getFocusedFormCaption()
            if s != '':
                # the following code does not seem to behave like it did previously, it does not go trough detached windows anymore
                # I asked about this in https://forum.image-line.com/viewtopic.php?t=340922
                self._screenBehavior.OnSendTempMsg(mcu_constants.ArrowsStr + 'Current window: ' + s)
        elif jogsrc in [mcu_buttons.Pattern, mcu_buttons.Mixer, mcu_buttons.Channels]:
            self.TrackSel(jogsrc - mcu_buttons.Pattern, event.outEv)
            if jogsrc == mcu_buttons.Pattern:
                ui.showWindow(midi.widPlaylist)
                ui.setFocused(midi.widPlaylist)
            elif jogsrc == mcu_buttons.Mixer:
                ui.showWindow(midi.widMixer)
                ui.setFocused(midi.widMixer)
            elif jogsrc == mcu_buttons.Channels:
                ui.showWindow(midi.widChannelRack)
                ui.setFocused(midi.widChannelRack)
        elif jogsrc == mcu_buttons.Tempo:
            if event.outEv != 0:
                general.processRECEvent(midi.REC_Tempo, channels.incEventValue(midi.REC_Tempo, event.outEv, midi.EKRes), midi.PME_RECFlagsT[int(event.pmeFlags & midi.PME_LiveInput != 0)] - midi.REC_FromMIDI)
            self._screenBehavior.OnSendTempMsg(mcu_constants.ArrowsStr + 'Tempo: ' + mixer.getEventIDValueString(midi.REC_Tempo, int(mixer.getCurrentTempo())))
        elif jogsrc in [mcu_buttons.Free1, mcu_buttons.Free2, mcu_buttons.Free3, mcu_buttons.Free4]:
            event.data1 = 390 + jogsrc - mcu_buttons.Free1
            if event.outEv != 0:
                event.isIncrement = 1
                s = chr(0x2B + int(event.outEv < 0) * 2)
                self._screenBehavior.OnSendTempMsg(mcu_constants.ArrowsStr + 'Free jog ' + str(event.data1) + ': ' + s)
                device.processMIDICC(event)
                return
            else:
                self._screenBehavior.OnSendTempMsg(mcu_constants.ArrowsStr + 'Free jog ' + str(event.data1))
