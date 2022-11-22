# name=FLtouch X-Touch
# url=https://github.com/bramdebouvere/fltouch
# supportedDevices=X-Touch

import patterns
import mixer
import device
import transport
import arrangement
import general
import launchMapPages
import playlist
import ui
import channels

import midi
import utils

import debug
import mcu_pages
import mcu_buttons
import mcu_device
import mcu_device_fader_conversion
import mcu_track
import mcu_extender_location
import mcu_base_class
import mcu_constants


class TMackieCU(mcu_base_class.McuBaseClass):
    def __init__(self):
        super().__init__(mcu_device.McuDevice(False))

        self.JogSource = 0

        self.Tracks = [mcu_track.McuTrack() for i in range(9)]

        self.Scrub = False

        self.MackieCU_ExtenderPosT = ('left', 'right')

        self.ExtenderPos = mcu_extender_location.Left

    def OnInit(self):
        super().OnInit()

        self.UpdateMeterMode()

        self.SetPage(self.Page)
        self.OnSendMsg('Linked to ' + ui.getProgTitle() +
                       ' (' + ui.getVersion() + ')')
        print('OnInit ready')

    def OnDeInit(self):
        super().OnDeInit()

        if device.isAssigned():
            # clear time message
            self.McuDevice.TimeDisplay.SetMessage('', skipIsAssignedCheck=True)
            # clear assignment message
            self.McuDevice.SetAssignmentMessage(skipIsAssignedCheck=True)

        print('OnDeInit ready')

    def OnRefresh(self, flags):

        if flags & midi.HW_Dirty_Mixer_Sel:
            self.UpdateMixer_Sel()

        if flags & midi.HW_Dirty_Mixer_Display:
            self.UpdateTextDisplay()
            self.UpdateColT()

        if flags & midi.HW_Dirty_Mixer_Controls:
            for n in range(0, len(self.Tracks)):
                if self.Tracks[n].Dirty:
                    self.UpdateCol(n)

        # LEDs
        if flags & midi.HW_Dirty_LEDs:
            self.UpdateLEDs()

    def TrackSel(self, Index, Step):

        Index = 2 - Index
        device.baseTrackSelect(Index, Step)
        if Index == 0:
            s = channels.getChannelName(channels.channelNumber())
            self.OnSendMsg(mcu_constants.ArrowsStr + 'Channel: ' + s)
        elif Index == 1:
            self.OnSendMsg(mcu_constants.ArrowsStr + 'Mixer track: ' +
                           mixer.getTrackName(mixer.trackNumber()))
        elif Index == 2:
            s = patterns.getPatternName(patterns.patternNumber())
            self.OnSendMsg(mcu_constants.ArrowsStr + 'Pattern: ' + s)

    def Jog(self, event):
        if self.JogSource == 0:
            if (ui.getFocused(midi.widBrowser)):
                # go up/down in browser
                transport.globalTransport(
                    midi.FPT_Jog, event.outEv, event.pmeFlags)
            else:
                ui.showWindow(midi.widPlaylist)
                ui.setFocused(midi.widPlaylist)
                if (self.Scrub):
                    oldSongPos = transport.getSongPos(midi.SONGLENGTH_ABSTICKS)
                    transport.setSongPos(
                        oldSongPos + event.outEv * (1 + 9 * (not self.Shift)), midi.SONGLENGTH_ABSTICKS)
                else:
                    transport.globalTransport(
                        midi.FPT_Jog, event.outEv, event.pmeFlags)  # relocate
        elif self.JogSource == mcu_buttons.Move:
            transport.globalTransport(
                midi.FPT_MoveJog, event.outEv, event.pmeFlags)
        elif self.JogSource == mcu_buttons.Marker:
            ui.showWindow(midi.widPlaylist)
            ui.setFocused(midi.widPlaylist)
            if self.Shift:
                s = 'Marker selection'
            else:
                s = 'Marker jump'
            if event.outEv != 0:
                if transport.globalTransport(midi.FPT_MarkerJumpJog + int(self.Shift), event.outEv, event.pmeFlags) == midi.GT_Global:
                    s = ui.getHintMsg()
            self.OnSendMsg(mcu_constants.ArrowsStr + s)

        elif self.JogSource == mcu_buttons.Undo:
            if event.outEv == 0:
                s = 'Undo history'
            elif transport.globalTransport(midi.FPT_UndoJog, event.outEv, event.pmeFlags) == midi.GT_Global:
                s = ui.getHintMsg()
            self.OnSendMsg(mcu_constants.ArrowsStr + s +
                           ' (level ' + general.getUndoLevelHint() + ')')

        elif self.JogSource == mcu_buttons.Zoom:
            if event.outEv != 0:
                transport.globalTransport(
                    midi.FPT_HZoomJog + int(self.Shift), event.outEv, event.pmeFlags)

        elif self.JogSource == mcu_buttons.Window:
            if event.outEv != 0:
                transport.globalTransport(
                    midi.FPT_WindowJog, event.outEv, event.pmeFlags)
            s = ui.getFocusedFormCaption()
            if s != "":
                self.OnSendMsg(mcu_constants.ArrowsStr +
                               'Current window: ' + s)

        elif (self.JogSource == mcu_buttons.Pattern) | (self.JogSource == mcu_buttons.Mixer) | (self.JogSource == mcu_buttons.Channels):
            self.TrackSel(self.JogSource - mcu_buttons.Pattern, event.outEv)
            if (self.JogSource == mcu_buttons.Pattern):
                ui.showWindow(midi.widPlaylist)
                ui.setFocused(midi.widPlaylist)
            elif (self.JogSource == mcu_buttons.Mixer):
                ui.showWindow(midi.widMixer)
                ui.setFocused(midi.widMixer)
            elif (self.JogSource == mcu_buttons.Channels):
                ui.showWindow(midi.widChannelRack)
                ui.setFocused(midi.widChannelRack)

        elif self.JogSource == mcu_buttons.Tempo:
            if event.outEv != 0:
                channels.processRECEvent(midi.REC_Tempo, channels.incEventValue(
                    midi.REC_Tempo, event.outEv, midi.EKRes), midi.PME_RECFlagsT[int(event.pmeFlags & midi.PME_LiveInput != 0)] - midi.REC_FromMIDI)
            self.OnSendMsg(mcu_constants.ArrowsStr + 'Tempo: ' +
                           mixer.getEventIDValueString(midi.REC_Tempo, mixer.getCurrentTempo()))

        elif self.JogSource in [mcu_buttons.Free1, mcu_buttons.Free2, mcu_buttons.Free3, mcu_buttons.Free4]:
            # CC
            event.data1 = 390 + self.JogSource - mcu_buttons.Free1

            if event.outEv != 0:
                event.isIncrement = 1
                # + or - sign depending on how you rotate
                s = chr(0x2B + int(event.outEv < 0)*2)
                self.OnSendMsg(mcu_constants.ArrowsStr +
                               'Free jog ' + str(event.data1) + ': ' + s)
                device.processMIDICC(event)
                return
            else:
                self.OnSendMsg(mcu_constants.ArrowsStr +
                               'Free jog ' + str(event.data1))

    def OnMidiMsg(self, event):
        if (event.midiId == midi.MIDI_CONTROLCHANGE):
            if (event.midiChan == 0):
                event.inEv = event.data2
                if event.inEv >= 0x40:
                    event.outEv = -(event.inEv - 0x40)
                else:
                    event.outEv = event.inEv

                if event.data1 == 0x3C:
                    self.Jog(event)
                    event.handled = True
                # knobs
                elif event.data1 in [0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17]:
                    Res = 0.005 + ((abs(event.outEv)-1) / 2000)
                    if self.Page == mcu_pages.Free:
                        i = event.data1 - 0x10
                        event.data1 = self.Tracks[i].BaseEventID + \
                            int(self.Tracks[i].KnobHeld)
                        event.isIncrement = 1
                        # + or - sign depending on how you rotate
                        s = chr(0x2B + int(event.outEv < 0)*2)
                        self.OnSendMsg(
                            'Free knob ' + str(event.data1) + ': ' + s + str(abs(event.outEv)))
                        device.processMIDICC(event)
                        device.hardwareRefreshMixerTrack(
                            self.Tracks[i].TrackNum)
                    else:
                        self.SetKnobValue(event.data1 - 0x10, event.outEv, Res)
                        event.handled = True
                else:
                    event.handled = False  # for extra CCs in emulators
            else:
                event.handled = False  # for extra CCs in emulators

        elif event.midiId == midi.MIDI_PITCHBEND:  # pitch bend (faders)

            # midiChan is the number of the fader (0-8)
            if event.midiChan <= 8:
                event.inEv = event.data1 + (event.data2 << 7)
                event.outEv = (event.inEv << 16) // 16383
                event.inEv -= 0x2000

                if self.Page == mcu_pages.Free:
                    self.FreeCtrlT[self.Tracks[event.midiChan]
                                   .TrackNum] = event.data1 + (event.data2 << 7)
                    device.hardwareRefreshMixerTrack(
                        self.Tracks[event.midiChan].TrackNum)
                    event.data1 = self.Tracks[event.midiChan].BaseEventID + 7
                    event.midiChan = 0
                    event.midiChanEx = 0
                    self.OnSendMsg('Free slider ' + str(event.data1) +
                                   ': ' + ui.getHintValue(event.outEv, 65523))
                    event.status = event.midiId = midi.MIDI_CONTROLCHANGE
                    event.isIncrement = 0
                    event.outEv = int(event.data2 / 127.0 * midi.FromMIDI_Max)
                    device.processMIDICC(event)
                elif self.Tracks[event.midiChan].SliderEventID >= 0:
                    # slider (mixer track volume)
                    event.handled = True
                    mixer.automateEvent(self.Tracks[event.midiChan].SliderEventID, mcu_device_fader_conversion.McuFaderToFlFader(
                        event.inEv + 0x2000), midi.REC_MIDIController, self.SmoothSpeed)
                    # hint
                    n = mixer.getAutoSmoothEventValue(
                        self.Tracks[event.midiChan].SliderEventID)
                    s = mixer.getEventIDValueString(
                        self.Tracks[event.midiChan].SliderEventID, n)
                    if s != '':
                        s = ': ' + s
                    self.OnSendMsg(self.Tracks[event.midiChan].SliderName + s)

        elif (event.midiId == midi.MIDI_NOTEON) | (event.midiId == midi.MIDI_NOTEOFF):  # NOTE
            if event.midiId == midi.MIDI_NOTEON:
                # slider hold
                if (event.data1 in [mcu_buttons.Slider_1, mcu_buttons.Slider_2, mcu_buttons.Slider_3, mcu_buttons.Slider_4, mcu_buttons.Slider_5, mcu_buttons.Slider_6, mcu_buttons.Slider_7, mcu_buttons.Slider_8, mcu_buttons.Slider_Main]):
                    # Auto select channel
                    if event.data1 != mcu_buttons.Slider_Main and event.data2 > 0 and (self.Page == mcu_pages.Pan or self.Page == mcu_pages.Stereo):
                        fader_index = event.data1 - mcu_buttons.Slider_1
                        if mixer.trackNumber != self.Tracks[fader_index].TrackNum:
                            mixer.setTrackNumber(
                                self.Tracks[fader_index].TrackNum)
                    event.handled = True
                    return

                if (event.pmeFlags & midi.PME_System != 0):
                    # F1..F8
                    if self.Shift & (event.data1 in [mcu_buttons.Cut, mcu_buttons.Copy, mcu_buttons.Paste, mcu_buttons.Insert, mcu_buttons.Delete, mcu_buttons.ItemMenu, mcu_buttons.Undo, mcu_buttons.UndoRedo]):
                        transport.globalTransport(
                            midi.FPT_F1 - mcu_buttons.Cut + event.data1, int(event.data2 > 0) * 2, event.pmeFlags)
                        event.data1 = 0xFF

                    if event.data1 == mcu_buttons.NameValue:  # display mode
                        if event.data2 > 0:
                            if self.Shift:
                                self.ExtenderPos = abs(self.ExtenderPos - 1)
                                self.FirstTrackT[self.FirstTrack] = 1
                                self.SetPage(self.Page)
                                self.OnSendMsg(
                                    'Extender on ' + self.MackieCU_ExtenderPosT[self.ExtenderPos])
                            else:
                                transport.globalTransport(midi.FPT_F2, int(
                                    event.data2 > 0) * 2, event.pmeFlags, 8)
                    elif event.data1 == mcu_buttons.TimeFormat:  # time format
                        if event.data2 > 0:
                            ui.setTimeDispMin()
                    elif (event.data1 == mcu_buttons.FaderBankLeft) | (event.data1 == mcu_buttons.FaderBankRight):  # mixer bank
                        if event.data2 > 0:
                            self.SetFirstTrack(
                                self.FirstTrackT[self.FirstTrack] - 8 + int(event.data1 == mcu_buttons.FaderBankRight) * 16)
                            self.McuDevice.SendMidiToExtender(
                                midi.MIDI_NOTEON + (event.data1 << 8) + (event.data2 << 16))
                    elif (event.data1 == mcu_buttons.FaderChannelLeft) | (event.data1 == mcu_buttons.FaderChannelRight):
                        if event.data2 > 0:
                            self.SetFirstTrack(self.FirstTrackT[self.FirstTrack] - 1 + int(
                                event.data1 == mcu_buttons.FaderChannelRight) * 2)
                            self.McuDevice.SendMidiToExtender(
                                midi.MIDI_NOTEON + (event.data1 << 8) + (event.data2 << 16))
                    elif event.data1 == mcu_buttons.Flip:  # self.Flip
                        if event.data2 > 0:
                            self.Flip = not self.Flip
                            self.McuDevice.SendMidiToExtender(
                                midi.MIDI_NOTEON + (event.data1 << 8) + (event.data2 << 16))
                            self.UpdateColT()
                            self.UpdateLEDs()
                    elif event.data1 == mcu_buttons.Smooth:  # smoothing
                        if event.data2 > 0:
                            self.SmoothSpeed = int(self.SmoothSpeed == 0) * 469
                            self.UpdateLEDs()
                            self.OnSendMsg(
                                'Control smoothing ' + mcu_constants.OffOnStr[int(self.SmoothSpeed > 0)])
                    elif event.data1 == mcu_buttons.Scrub:  # self.Scrub
                        if event.data2 > 0:
                            self.Scrub = not self.Scrub
                            self.UpdateLEDs()
                    # jog sources
                    elif event.data1 in [mcu_buttons.Undo, mcu_buttons.Pattern, mcu_buttons.Mixer, mcu_buttons.Channels, mcu_buttons.Tempo, mcu_buttons.Free1, mcu_buttons.Free2, mcu_buttons.Free3, mcu_buttons.Free4, mcu_buttons.Marker, mcu_buttons.Zoom, mcu_buttons.Move, mcu_buttons.Window]:
                        # update jog source
                        if event.data1 in [mcu_buttons.Zoom, mcu_buttons.Window]:
                            device.directFeedback(event)
                        if event.data2 == 0:
                            if self.JogSource == event.data1:
                                self.SetJogSource(0)
                        else:
                            self.SetJogSource(event.data1)
                            event.outEv = 0
                            self.Jog(event)  # for visual feedback

                    # arrows
                    elif event.data1 in [mcu_buttons.Up, mcu_buttons.Down, mcu_buttons.Left, mcu_buttons.Right]:
                        if self.JogSource == 0:
                            transport.globalTransport(
                                midi.FPT_Up - mcu_buttons.Up + event.data1, int(event.data2 > 0) * 2, event.pmeFlags)
                        else:
                            if event.data2 > 0:
                                ArrowStepT = [2, -2, -1, 1]
                                event.inEv = ArrowStepT[event.data1 -
                                                        mcu_buttons.Up]
                                event.outEv = event.inEv
                                self.Jog(event)

                    elif event.data1 in [mcu_buttons.Pan, mcu_buttons.Sends, mcu_buttons.Equalizer, mcu_buttons.Stereo, mcu_buttons.Effects, mcu_buttons.Free]:  # self.Page
                        if event.data2 > 0:
                            n = event.data1 - mcu_buttons.Pan
                            self.OnSendMsg(mcu_constants.PageDescriptions[n])
                            self.SetPage(n)
                            self.McuDevice.SendMidiToExtender(
                                midi.MIDI_NOTEON + (event.data1 << 8) + (event.data2 << 16))

                    elif event.data1 == mcu_buttons.Shift:  # self.Shift
                        self.Shift = event.data2 > 0
                        device.directFeedback(event)

                    elif event.data1 == mcu_buttons.Edison:  # open audio editor in current mixer track
                        device.directFeedback(event)
                        if event.data2 > 0:
                            ui.launchAudioEditor(
                                False, '', mixer.trackNumber(), 'AudioLoggerTrack.fst', '')
                            self.OnSendMsg('Audio editor ready')

                    elif event.data1 == mcu_buttons.Metronome:  # metronome/button self.Clicking
                        if event.data2 > 0:
                            if self.Shift:
                                self.Clicking = not self.Clicking
                                self.McuDevice.SetClicking(self.Clicking)
                                self.OnSendMsg(
                                    'Clicking ' + mcu_constants.OffOnStr[self.Clicking])
                            else:
                                transport.globalTransport(
                                    midi.FPT_Metronome, 1, event.pmeFlags)

                    elif event.data1 == mcu_buttons.CountDown:  # precount
                        if event.data2 > 0:
                            transport.globalTransport(
                                midi.FPT_CountDown, 1, event.pmeFlags)

                    # cut/copy/paste/insert/delete
                    elif event.data1 in [mcu_buttons.Cut, mcu_buttons.Copy, mcu_buttons.Paste, mcu_buttons.Insert, mcu_buttons.Delete]:
                        transport.globalTransport(
                            midi.FPT_Cut + event.data1 - mcu_buttons.Cut, int(event.data2 > 0) * 2, event.pmeFlags)
                        if event.data2 > 0:
                            # FPT_Cut..FPT_Delete
                            CutCopyMsgT = (
                                'Cut', 'Copy', 'Paste', 'Insert', 'Delete')
                            self.OnSendMsg(
                                CutCopyMsgT[midi.FPT_Cut + event.data1 - mcu_buttons.Cut - 50])

                    elif (event.data1 == mcu_buttons.Rewind) | (event.data1 == mcu_buttons.FastForward):  # << >>
                        if self.Shift:
                            if event.data2 == 0:
                                v2 = 1
                            elif event.data1 == mcu_buttons.Rewind:
                                v2 = 0.5
                            else:
                                v2 = 2
                            transport.setPlaybackSpeed(v2)
                        else:
                            transport.globalTransport(
                                midi.FPT_Rewind + int(event.data1 == 0x5C), int(event.data2 > 0) * 2, event.pmeFlags)
                        device.directFeedback(event)

                    elif event.data1 == mcu_buttons.Stop:  # stop
                        transport.globalTransport(midi.FPT_Stop, int(
                            event.data2 > 0) * 2, event.pmeFlags)
                    elif event.data1 == mcu_buttons.Play:  # play
                        transport.globalTransport(midi.FPT_Play, int(
                            event.data2 > 0) * 2, event.pmeFlags)
                    elif event.data1 == mcu_buttons.Record:  # record
                        transport.globalTransport(midi.FPT_Record, int(
                            event.data2 > 0) * 2, event.pmeFlags)
                    elif event.data1 == mcu_buttons.SongVSLoop:  # song/loop
                        transport.globalTransport(midi.FPT_Loop, int(
                            event.data2 > 0) * 2, event.pmeFlags)
                    elif event.data1 == mcu_buttons.Mode:  # mode
                        transport.globalTransport(midi.FPT_Mode, int(
                            event.data2 > 0) * 2, event.pmeFlags)
                        device.directFeedback(event)

                    elif event.data1 == mcu_buttons.Snap:  # snap
                        if self.Shift:
                            if event.data2 > 0:
                                transport.globalTransport(
                                    midi.FPT_SnapMode, 1, event.pmeFlags)
                        else:
                            transport.globalTransport(midi.FPT_Snap, int(
                                event.data2 > 0) * 2, event.pmeFlags)

                    elif event.data1 == mcu_buttons.Escape:  # ESC
                        transport.globalTransport(
                            midi.FPT_Escape + int(self.Shift) * 2, int(event.data2 > 0) * 2, event.pmeFlags)
                    elif event.data1 == mcu_buttons.Enter:  # ENTER
                        transport.globalTransport(
                            midi.FPT_Enter + int(self.Shift) * 2, int(event.data2 > 0) * 2, event.pmeFlags)
                    elif event.data1 in [mcu_buttons.Encoder_1, mcu_buttons.Encoder_2, mcu_buttons.Encoder_3, mcu_buttons.Encoder_4, mcu_buttons.Encoder_5, mcu_buttons.Encoder_6, mcu_buttons.Encoder_7, mcu_buttons.Encoder_8]:  # knob reset
                        if self.Page == mcu_pages.Free:
                            i = event.data1 - mcu_buttons.Encoder_1
                            self.Tracks[i].KnobHeld = event.data2 > 0
                            if event.data2 > 0:
                                event.data1 = self.Tracks[i].BaseEventID + 2
                                event.outEv = 0
                                event.isIncrement = 2
                                self.OnSendMsg(
                                    'Free knob switch ' + str(event.data1))
                                device.processMIDICC(event)
                            device.hardwareRefreshMixerTrack(
                                self.Tracks[i].TrackNum)
                            return
                        elif event.data2 > 0:
                            n = event.data1 - mcu_buttons.Encoder_1
                            if self.Page == mcu_pages.Sends:
                                if mixer.setRouteTo(mixer.trackNumber(), self.Tracks[n].TrackNum, -1) < 0:
                                    self.OnSendMsg('Cannot send to this track')
                                else:
                                    mixer.afterRoutingChanged()
                            else:
                                self.SetKnobValue(n, midi.MaxInt)

                    elif (event.data1 >= 0) & (event.data1 <= 0x1F):  # free hold buttons
                        if self.Page == mcu_pages.Free:
                            i = event.data1 % 8
                            event.data1 = self.Tracks[i].BaseEventID + \
                                3 + event.data1 // 8
                            event.inEv = event.data2
                            event.outEv = int(event.inEv > 0) * \
                                midi.FromMIDI_Max
                            self.OnSendMsg(
                                'Free button ' + str(event.data1) + ': ' + mcu_constants.OffOnStr[event.outEv > 0])
                            device.processMIDICC(event)
                            device.hardwareRefreshMixerTrack(
                                self.Tracks[i].TrackNum)
                            return

                    if (event.pmeFlags & midi.PME_System_Safe != 0):
                        # link selected channels from the channel rack to current mixer track
                        if event.data1 == mcu_buttons.LinkChannel:
                            if event.data2 > 0:
                                if self.Shift:
                                    mixer.linkTrackToChannel(
                                        midi.ROUTE_StartingFromThis)
                                else:
                                    mixer.linkTrackToChannel(midi.ROUTE_ToThis)
                        elif event.data1 == mcu_buttons.Browser:  # focus browser
                            if event.data2 > 0:
                                ui.showWindow(midi.widBrowser)

                        elif event.data1 == mcu_buttons.StepSequencer:  # focus step seq
                            if event.data2 > 0:
                                ui.showWindow(midi.widChannelRack)

                        elif event.data1 == mcu_buttons.Menu:  # menu
                            transport.globalTransport(midi.FPT_Menu, int(
                                event.data2 > 0) * 2, event.pmeFlags)
                            if event.data2 > 0:
                                self.OnSendMsg('Menu')

                        elif event.data1 == mcu_buttons.ItemMenu:  # tools
                            transport.globalTransport(midi.FPT_ItemMenu, int(
                                event.data2 > 0) * 2, event.pmeFlags)
                            if event.data2 > 0:
                                self.OnSendMsg('Tools')

                        elif event.data1 == mcu_buttons.UndoRedo:  # undo/redo
                            if (transport.globalTransport(midi.FPT_Undo, int(event.data2 > 0) * 2, event.pmeFlags) == midi.GT_Global) & (event.data2 > 0):
                                self.OnSendMsg(
                                    ui.getHintMsg() + ' (level ' + general.getUndoLevelHint() + ')')

                        # punch in/punch out/punch
                        elif event.data1 in [mcu_buttons.In, mcu_buttons.Out, mcu_buttons.Select]:
                            if event.data1 == mcu_buttons.Select:
                                n = midi.FPT_Punch
                            else:
                                n = midi.FPT_PunchIn + event.data1 - mcu_buttons.In
                            if not ((event.data1 == mcu_buttons.In) & (event.data2 == 0)):
                                device.directFeedback(event)
                            if (event.data1 >= mcu_buttons.Out) & (event.data2 >= int(event.data1 == mcu_buttons.Out)):
                                if device.isAssigned():
                                    device.midiOutMsg(
                                        (mcu_buttons.In << 8) + midi.TranzPort_OffOnT[False])
                            if transport.globalTransport(n, int(event.data2 > 0) * 2, event.pmeFlags) == midi.GT_Global:
                                t = -1
                                if n == midi.FPT_Punch:
                                    if event.data2 != 1:
                                        t = int(event.data2 != 2)
                                elif event.data2 > 0:
                                    t = int(n == midi.FPT_PunchOut)
                                if t >= 0:
                                    self.OnSendMsg(ui.getHintMsg())

                        elif event.data1 == mcu_buttons.AddMarker:  # marker add
                            if (transport.globalTransport(midi.FPT_AddMarker + int(self.Shift), int(event.data2 > 0) * 2, event.pmeFlags) == midi.GT_Global) & (event.data2 > 0):
                                self.OnSendMsg(ui.getHintMsg())

                        # select mixer track buttons
                        elif (event.data1 >= mcu_buttons.Select_1) & (event.data1 <= mcu_buttons.Select_8):
                            if event.data2 > 0:
                                i = event.data1 - mcu_buttons.Select_1

                                ui.showWindow(midi.widMixer)
                                mixer.setTrackNumber(
                                    self.Tracks[i].TrackNum, midi.curfxScrollToMakeVisible | midi.curfxMinimalLatencyUpdate)

                        # solo buttons
                        elif (event.data1 >= mcu_buttons.Solo_1) & (event.data1 <= mcu_buttons.Solo_8):
                            if event.data2 > 0:
                                i = event.data1 - mcu_buttons.Solo_1
                                self.Tracks[i].solomode = midi.fxSoloModeWithDestTracks
                                if self.Shift:
                                    # function does not exist: Include(self.Tracks[i].solomode, midi.fxSoloModeWithSourceTracks)
                                    pass
                                mixer.soloTrack(
                                    self.Tracks[i].TrackNum, midi.fxSoloToggle, self.Tracks[i].solomode)
                                mixer.setTrackNumber(
                                    self.Tracks[i].TrackNum, midi.curfxScrollToMakeVisible)

                        # mute buttons
                        elif (event.data1 >= mcu_buttons.Mute_1) & (event.data1 <= mcu_buttons.Mute_8):
                            if event.data2 > 0:
                                mixer.enableTrack(
                                    self.Tracks[event.data1 - mcu_buttons.Mute_1].TrackNum)

                        # record (arm) buttons
                        elif (event.data1 >= mcu_buttons.Record_1) & (event.data1 <= mcu_buttons.Record_8):
                            if event.data2 > 0:
                                mixer.armTrack(
                                    self.Tracks[event.data1].TrackNum)
                                if mixer.isTrackArmed(self.Tracks[event.data1].TrackNum):
                                    self.OnSendMsg(mixer.getTrackName(
                                        self.Tracks[event.data1].TrackNum) + ' recording to ' + mixer.getTrackRecordingFileName(self.Tracks[event.data1].TrackNum))
                                else:
                                    self.OnSendMsg(mixer.getTrackName(
                                        self.Tracks[event.data1].TrackNum) + ' unarmed')

                        # save/save new
                        elif event.data1 == mcu_buttons.Save:
                            transport.globalTransport(
                                midi.FPT_Save + int(self.Shift), int(event.data2 > 0) * 2, event.pmeFlags)

                        event.handled = True
                else:
                    event.handled = False
            else:
                event.handled = False

    def UpdateMsg(self):
        self.McuDevice.SetTextDisplay(self.MsgT[1])

    def OnSendMsg(self, Msg):
        self.MsgT[1] = Msg
        self.MsgDirty = True

    def OnUpdateBeatIndicator(self, Value):

        SyncLEDMsg = [midi.MIDI_NOTEON + (0x5E << 8), midi.MIDI_NOTEON + (
            0x5E << 8) + (0x7F << 16), midi.MIDI_NOTEON + (0x5E << 8) + (0x7F << 16)]

        if device.isAssigned():
            device.midiOutNewMsg(SyncLEDMsg[Value], 128)

    def SetPage(self, Value):

        oldPage = self.Page
        self.Page = Value

        self.FirstTrack = int(self.Page == mcu_pages.Free)
        receiverCount = device.dispatchReceiverCount()
        if receiverCount == 0:
            self.SetFirstTrack(self.FirstTrackT[self.FirstTrack])
        elif self.Page == oldPage:
            if self.ExtenderPos == mcu_extender_location.Left:
                for n in range(0, receiverCount):
                    device.dispatch(n, midi.MIDI_NOTEON + (0x7F << 8) +
                                    (self.FirstTrackT[self.FirstTrack] + (n * 8) << 16))
                self.SetFirstTrack(
                    self.FirstTrackT[self.FirstTrack] + receiverCount * 8)
            elif self.ExtenderPos == mcu_extender_location.Right:
                self.SetFirstTrack(self.FirstTrackT[self.FirstTrack])
                for n in range(0, receiverCount):
                    device.dispatch(n, midi.MIDI_NOTEON + (0x7F << 8) +
                                    (self.FirstTrackT[self.FirstTrack] + ((n + 1) * 8) << 16))

        if self.Page == mcu_pages.Free:

            BaseID = midi.EncodeRemoteControlID(
                device.getPortNumber(), 0, mcu_constants.FreeEventID + 7)
            for n in range(0, len(self.FreeCtrlT)):
                d = mixer.remoteFindEventValue(BaseID + n * 8, 1)
                if d >= 0:
                    self.FreeCtrlT[n] = min(round(d * 16384), 16384)

        if (oldPage == mcu_pages.Free) | (self.Page == mcu_pages.Free):
            self.UpdateMeterMode()
        self.UpdateColT()
        self.UpdateLEDs()
        self.UpdateTextDisplay()

    def UpdateMixer_Sel(self):

        if self.Page != mcu_pages.Free:
            if device.isAssigned():
                for m in range(0, len(self.Tracks) - 1):
                    device.midiOutNewMsg(
                        ((0x18 + m) << 8) + midi.TranzPort_OffOnT[self.Tracks[m].TrackNum == mixer.trackNumber()], self.Tracks[m].LastValueIndex + 4)

            if self.Page in [mcu_pages.Sends, mcu_pages.Effects]:
                self.UpdateColT()

    def UpdateCol(self, Num):

        data1 = 0
        data2 = 0
        baseID = 0
        center = 0
        b = False

        if device.isAssigned():
            if self.Page == mcu_pages.Free:
                baseID = midi.EncodeRemoteControlID(
                    device.getPortNumber(), 0, self.Tracks[Num].BaseEventID)
                # slider
                m = self.FreeCtrlT[self.Tracks[Num].TrackNum]
                device.midiOutNewMsg(midi.MIDI_PITCHBEND + Num + ((m & 0x7F) << 8) + (
                    (m >> 7) << 16), self.Tracks[Num].LastValueIndex + 5)
                if Num < 8:
                    # ring
                    d = mixer.remoteFindEventValue(
                        baseID + int(self.Tracks[Num].KnobHeld))
                    if d >= 0:
                        m = 1 + round(d * 10)
                    else:
                        m = int(self.Tracks[Num].KnobHeld) * (11 + (2 << 4))
                    device.midiOutNewMsg(
                        midi.MIDI_CONTROLCHANGE + ((0x30 + Num) << 8) + (m << 16), self.Tracks[Num].LastValueIndex)
                    # buttons
                    for n in range(0, 4):
                        d = mixer.remoteFindEventValue(baseID + 3 + n)
                        if d >= 0:
                            b = d >= 0.5
                        else:
                            b = False

                        device.midiOutNewMsg(
                            ((n * 8 + Num) << 8) + midi.TranzPort_OffOnT[b], self.Tracks[Num].LastValueIndex + 1 + n)
            else:
                sv = mixer.getEventValue(self.Tracks[Num].SliderEventID)

                if Num < 8:
                    # V-Pot
                    center = self.Tracks[Num].KnobCenter
                    if self.Tracks[Num].KnobEventID >= 0:
                        m = mixer.getEventValue(
                            self.Tracks[Num].KnobEventID, midi.MaxInt, False)
                        if center < 0:
                            if self.Tracks[Num].KnobResetEventID == self.Tracks[Num].KnobEventID:
                                center = int(
                                    m != self.Tracks[Num].KnobResetValue)
                            else:
                                center = int(
                                    sv != self.Tracks[Num].KnobResetValue)

                        if self.Tracks[Num].KnobMode < 2:
                            data1 = 1 + round(m * (10 / midi.FromMIDI_Max))
                        else:
                            data1 = round(m * (11 / midi.FromMIDI_Max))
                        if self.Tracks[Num].KnobMode > 3:
                            data1 = (center << 6)
                        else:
                            data1 = data1 + \
                                (self.Tracks[Num].KnobMode <<
                                 4) + (center << 6)
                    else:
                        data1 = 0

                    device.midiOutNewMsg(midi.MIDI_CONTROLCHANGE + ((0x30 + Num) << 8) + (
                        data1 << 16), self.Tracks[Num].LastValueIndex)

                    # arm, solo, mute
                    device.midiOutNewMsg(((0x00 + Num) << 8) + midi.TranzPort_OffOnBlinkT[int(mixer.isTrackArmed(
                        self.Tracks[Num].TrackNum)) * (1 + int(transport.isRecording()))], self.Tracks[Num].LastValueIndex + 1)
                    device.midiOutNewMsg(((0x08 + Num) << 8) + midi.TranzPort_OffOnT[mixer.isTrackSolo(
                        self.Tracks[Num].TrackNum)], self.Tracks[Num].LastValueIndex + 2)
                    device.midiOutNewMsg(((0x10 + Num) << 8) + midi.TranzPort_OffOnT[not mixer.isTrackEnabled(
                        self.Tracks[Num].TrackNum)], self.Tracks[Num].LastValueIndex + 3)

                # slider
                self.McuDevice.GetTrack(
                    Num).fader.SetLevelFromFlsFader(sv, True)

            self.Tracks[Num].Dirty = False

    def UpdateColT(self):
        f = self.FirstTrackT[self.FirstTrack]
        CurID = mixer.getTrackPluginId(mixer.trackNumber(), 0)

        for m in range(0, len(self.Tracks)):
            if self.Page == mcu_pages.Free:
                # free controls
                if m == 8:
                    self.Tracks[m].TrackNum = mcu_constants.FreeTrackCount
                else:
                    self.Tracks[m].TrackNum = (
                        f + m) % mcu_constants.FreeTrackCount

                self.Tracks[m].KnobName = 'Knob ' + \
                    str(self.Tracks[m].TrackNum + 1)
                self.Tracks[m].SliderName = 'Slider ' + \
                    str(self.Tracks[m].TrackNum + 1)

                self.Tracks[m].BaseEventID = mcu_constants.FreeEventID + \
                    self.Tracks[m].TrackNum * 8  # first virtual CC
            else:
                self.Tracks[m].KnobPressEventID = -1

                # mixer
                if m == 8:
                    self.Tracks[m].TrackNum = -2
                    self.Tracks[m].BaseEventID = midi.REC_MainVol
                    self.Tracks[m].SliderEventID = self.Tracks[m].BaseEventID
                    self.Tracks[m].SliderName = 'Master Vol'
                else:
                    self.Tracks[m].TrackNum = midi.TrackNum_Master + \
                        ((f + m) % mixer.trackCount())
                    self.Tracks[m].BaseEventID = mixer.getTrackPluginId(
                        self.Tracks[m].TrackNum, 0)
                    self.Tracks[m].SliderEventID = self.Tracks[m].BaseEventID + \
                        midi.REC_Mixer_Vol
                    s = mixer.getTrackName(self.Tracks[m].TrackNum)
                    self.Tracks[m].SliderName = s + ' - Vol'

                    self.Tracks[m].KnobEventID = -1
                    self.Tracks[m].KnobResetEventID = -1
                    self.Tracks[m].KnobResetValue = midi.FromMIDI_Max >> 1
                    self.Tracks[m].KnobName = ''
                    self.Tracks[m].KnobMode = 1  # parameter, pan, volume, off
                    self.Tracks[m].KnobCenter = -1

                    if self.Page == mcu_pages.Pan:
                        self.Tracks[m].KnobEventID = self.Tracks[m].BaseEventID + \
                            midi.REC_Mixer_Pan
                        self.Tracks[m].KnobResetEventID = self.Tracks[m].KnobEventID
                        self.Tracks[m].KnobName = mixer.getTrackName(
                            self.Tracks[m].TrackNum) + ' - ' + 'Pan'
                    elif self.Page == mcu_pages.Stereo:
                        self.Tracks[m].KnobEventID = self.Tracks[m].BaseEventID + \
                            midi.REC_Mixer_SS
                        self.Tracks[m].KnobResetEventID = self.Tracks[m].KnobEventID
                        self.Tracks[m].KnobName = mixer.getTrackName(
                            self.Tracks[m].TrackNum) + ' - ' + 'Sep'
                    elif self.Page == mcu_pages.Sends:
                        self.Tracks[m].KnobEventID = CurID + \
                            midi.REC_Mixer_Send_First + self.Tracks[m].TrackNum
                        s = mixer.getEventIDName(self.Tracks[m].KnobEventID)
                        self.Tracks[m].KnobName = s
                        self.Tracks[m].KnobResetValue = round(
                            12800 * midi.FromMIDI_Max / 16000)
                        self.Tracks[m].KnobCenter = mixer.getRouteSendActive(
                            mixer.trackNumber(), self.Tracks[m].TrackNum)
                        if self.Tracks[m].KnobCenter == 0:
                            self.Tracks[m].KnobMode = 4
                        else:
                            self.Tracks[m].KnobMode = 2
                    elif self.Page == mcu_pages.Effects:
                        CurID = mixer.getTrackPluginId(mixer.trackNumber(), m)
                        self.Tracks[m].KnobEventID = CurID + \
                            midi.REC_Plug_MixLevel
                        s = mixer.getEventIDName(self.Tracks[m].KnobEventID)
                        self.Tracks[m].KnobName = s
                        self.Tracks[m].KnobResetValue = midi.FromMIDI_Max

                        IsValid = mixer.isTrackPluginValid(
                            mixer.trackNumber(), m)
                        IsEnabledAuto = mixer.isTrackAutomationEnabled(
                            mixer.trackNumber(), m)
                        if IsValid:
                            self.Tracks[m].KnobMode = 2
                            self.Tracks[m].KnobPressEventID = CurID + \
                                midi.REC_Plug_Mute
                        else:
                            self.Tracks[m].KnobMode = 4
                        self.Tracks[m].KnobCenter = int(
                            IsValid & IsEnabledAuto)
                    elif self.Page == mcu_pages.Equalizer:
                        if m < 3:
                            # gain & freq
                            self.Tracks[m].SliderEventID = CurID + \
                                midi.REC_Mixer_EQ_Gain + m
                            self.Tracks[m].KnobResetEventID = self.Tracks[m].SliderEventID
                            s = mixer.getEventIDName(
                                self.Tracks[m].SliderEventID)
                            self.Tracks[m].SliderName = s
                            self.Tracks[m].KnobEventID = CurID + \
                                midi.REC_Mixer_EQ_Freq + m
                            s = mixer.getEventIDName(
                                self.Tracks[m].KnobEventID)
                            self.Tracks[m].KnobName = s
                            self.Tracks[m].KnobResetValue = midi.FromMIDI_Max >> 1
                            self.Tracks[m].KnobCenter = -2
                            self.Tracks[m].KnobMode = 0
                        else:
                            if m < 6:
                                # Q
                                self.Tracks[m].SliderEventID = CurID + \
                                    midi.REC_Mixer_EQ_Q + m - 3
                                self.Tracks[m].KnobResetEventID = self.Tracks[m].SliderEventID
                                s = mixer.getEventIDName(
                                    self.Tracks[m].SliderEventID)
                                self.Tracks[m].SliderName = s
                                self.Tracks[m].KnobEventID = self.Tracks[m].SliderEventID
                                self.Tracks[m].KnobName = self.Tracks[m].SliderName
                                self.Tracks[m].KnobResetValue = 17500
                                self.Tracks[m].KnobCenter = -1
                                self.Tracks[m].KnobMode = 2
                            else:
                                self.Tracks[m].SliderEventID = -1
                                self.Tracks[m].KnobEventID = -1
                                self.Tracks[m].KnobMode = 4

                    # self.Flip knob & slider
                    if self.Flip:
                        self.Tracks[m].KnobEventID, self.Tracks[m].SliderEventID = utils.SwapInt(
                            self.Tracks[m].KnobEventID, self.Tracks[m].SliderEventID)
                        s = self.Tracks[m].SliderName
                        self.Tracks[m].SliderName = self.Tracks[m].KnobName
                        self.Tracks[m].KnobName = s
                        self.Tracks[m].KnobMode = 2
                        if not (self.Page in [mcu_pages.Sends, mcu_pages.Effects, mcu_pages.Equalizer]):
                            self.Tracks[m].KnobCenter = -1
                            self.Tracks[m].KnobResetValue = round(
                                12800 * midi.FromMIDI_Max / 16000)
                            self.Tracks[m].KnobResetEventID = self.Tracks[m].KnobEventID

            self.Tracks[m].LastValueIndex = 48 + m * 6
            self.UpdateCol(m)

    def SetKnobValue(self, Num, Value, Res=midi.EKRes):

        if (self.Tracks[Num].KnobEventID >= 0) & (self.Tracks[Num].KnobMode < 4):
            if Value == midi.MaxInt:
                if self.Page == mcu_pages.Effects:
                    if self.Tracks[Num].KnobPressEventID >= 0:

                        Value = channels.incEventValue(
                            self.Tracks[Num].KnobPressEventID, 0, midi.EKRes)
                        channels.processRECEvent(
                            self.Tracks[Num].KnobPressEventID, Value, midi.REC_Controller)
                        s = mixer.getEventIDName(
                            self.Tracks[Num].KnobPressEventID)
                        self.OnSendMsg(s)
                    return
                else:
                    mixer.automateEvent(
                        self.Tracks[Num].KnobResetEventID, self.Tracks[Num].KnobResetValue, midi.REC_MIDIController, self.SmoothSpeed)
            else:
                mixer.automateEvent(
                    self.Tracks[Num].KnobEventID, Value, midi.REC_Controller, self.SmoothSpeed, 1, Res)

            # hint
            n = mixer.getAutoSmoothEventValue(self.Tracks[Num].KnobEventID)
            s = mixer.getEventIDValueString(self.Tracks[Num].KnobEventID, n)
            if s != '':
                s = ': ' + s
            self.OnSendMsg(self.Tracks[Num].KnobName + s)

    def SetFirstTrack(self, Value):

        if self.Page == mcu_pages.Free:
            self.FirstTrackT[self.FirstTrack] = (
                Value + mcu_constants.FreeTrackCount) % mcu_constants.FreeTrackCount
            firstTrackNumber = self.FirstTrackT[self.FirstTrack] + 1
        else:
            self.FirstTrackT[self.FirstTrack] = (
                Value + mixer.trackCount()) % mixer.trackCount()
            firstTrackNumber = self.FirstTrackT[self.FirstTrack]
        self.UpdateColT()
        self.McuDevice.SetAssignmentMessage(firstTrackNumber)
        device.hardwareRefreshMixerTrack(-1)

    def OnIdle(self):
        self.UpdateTimeDisplay()
        super().OnIdle()

    def UpdateTimeDisplay(self):
        """ Updates the time display to the current value """

        # time display
        if ui.getTimeDispMin():
            # HHH.MM.SS.CC_
            if playlist.getVisTimeBar() == -midi.MaxInt:
                s = '-   0'
            else:
                n = abs(playlist.getVisTimeBar())
                h, m = utils.DivModU(n, 60)
                # todo sign of...
                s = utils.Zeros_Strict(
                    (h * 100 + m) * utils.SignOf(playlist.getVisTimeBar()), 5, ' ')

            s = s + utils.Zeros_Strict(abs(playlist.getVisTimeStep()), 2) + \
                utils.Zeros_Strict(playlist.getVisTimeTick(), 2) + ' '
        else:
            # BBB.BB.__.TTT
            s = utils.Zeros_Strict(playlist.getVisTimeBar(), 3, ' ') + utils.Zeros_Strict(abs(
                playlist.getVisTimeStep()), 2) + '  ' + utils.Zeros_Strict(playlist.getVisTimeTick(), 3)

        self.McuDevice.TimeDisplay.SetMessage(s)

    def UpdateLEDs(self):

        if device.isAssigned():
            # stop
            device.midiOutNewMsg(
                (0x5D << 8) + midi.TranzPort_OffOnT[transport.isPlaying() == midi.PM_Stopped], 0)
            # loop
            device.midiOutNewMsg(
                (0x5A << 8) + midi.TranzPort_OffOnT[transport.getLoopMode() == midi.SM_Pat], 1)
            # record
            isRecording = transport.isRecording()
            device.midiOutNewMsg(
                (0x5F << 8) + midi.TranzPort_OffOnT[isRecording], 2)
            # SMPTE/BEATS
            device.midiOutNewMsg(
                (0x71 << 8) + midi.TranzPort_OffOnT[ui.getTimeDispMin()], 3)
            device.midiOutNewMsg(
                (0x72 << 8) + midi.TranzPort_OffOnT[not ui.getTimeDispMin()], 4)
            # self.Page
            for m in range(0,  6):
                device.midiOutNewMsg(
                    ((0x28 + m) << 8) + midi.TranzPort_OffOnT[m == self.Page], 5 + m)
            # changed flag
            device.midiOutNewMsg(
                (0x50 << 8) + midi.TranzPort_OffOnT[general.getChangedFlag() > 0], 11)
            # metronome
            device.midiOutNewMsg(
                (0x57 << 8) + midi.TranzPort_OffOnT[general.getUseMetronome()], 12)
            # rec precount
            device.midiOutNewMsg(
                (0x58 << 8) + midi.TranzPort_OffOnT[general.getPrecount()], 13)
            # self.Scrub
            device.midiOutNewMsg(
                (0x65 << 8) + midi.TranzPort_OffOnT[self.Scrub], 15)
            # use RUDE SOLO to show if any track is armed for recording
            b = 0
            for m in range(0,  mixer.trackCount()):
                if mixer.isTrackArmed(m):
                    b = 1 + int(isRecording)
                    break

            device.midiOutNewMsg(
                (0x73 << 8) + midi.TranzPort_OffOnBlinkT[b], 16)
            # smoothing
            device.midiOutNewMsg(
                (0x33 << 8) + midi.TranzPort_OffOnT[self.SmoothSpeed > 0], 17)
            # self.Flip
            device.midiOutNewMsg(
                (0x32 << 8) + midi.TranzPort_OffOnT[self.Flip], 18)
            # snap
            device.midiOutNewMsg(
                (0x56 << 8) + midi.TranzPort_OffOnT[ui.getSnapMode() != 3], 19)
            # focused windows
            device.midiOutNewMsg(
                (0x4A << 8) + midi.TranzPort_OffOnT[ui.getFocused(midi.widBrowser)], 20)
            device.midiOutNewMsg(
                (0x4B << 8) + midi.TranzPort_OffOnT[ui.getFocused(midi.widChannelRack)], 21)

    def SetJogSource(self, Value):
        self.JogSource = Value

    def OnWaitingForInput(self):
        """ Called when FL studio is in waiting mode """
        self.McuDevice.TimeDisplay.SetMessage('..........')


MackieCU = TMackieCU()


def OnInit():
    MackieCU.OnInit()


def OnDeInit():
    MackieCU.OnDeInit()


def OnDirtyMixerTrack(SetTrackNum):
    MackieCU.OnDirtyMixerTrack(SetTrackNum)


def OnRefresh(Flags):
    MackieCU.OnRefresh(Flags)


def OnMidiMsg(event):
    MackieCU.OnMidiMsg(event)


def OnSendTempMsg(Msg, Duration=1000):
    MackieCU.OnSendMsg(Msg)


def OnUpdateBeatIndicator(Value):
    MackieCU.OnUpdateBeatIndicator(Value)


def OnUpdateMeters():
    MackieCU.OnUpdateMeters()


def OnIdle():
    MackieCU.OnIdle()


def OnWaitingForInput():
    MackieCU.OnWaitingForInput()
