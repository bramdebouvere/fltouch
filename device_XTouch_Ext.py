# name=FLtouch X-Touch Extender
# url=https://forum.image-line.com/viewtopic.php?f=1994&t=269919
# receiveFrom=FLtouch X-Touch
# supportedDevices=X-Touch-Ext

import mixer
import device
import transport
import ui

import midi
import utils

import debug
import mcu_pages
import mcu_buttons
import mcu_device
import mcu_device_fader_conversion
import mcu_track
import mcu_base_class
import mcu_constants
import tracknames

class TMackieCU_Ext(mcu_base_class.McuBaseClass):
    def __init__(self):
        super().__init__(mcu_device.McuDevice(True))

        self.Tracks = [mcu_track.McuTrack() for i in range(9)] # TODO: this should probably be changed to 8, since there are only 8 faders on an extender

    def OnInit(self):
        super().OnInit()

        self.UpdateMeterMode()

        self.SetPage(self.Page)
        self.OnSendMsg('Linked to ' + ui.getProgTitle() + ' (' + ui.getVersion() + ')')
        print('OnInit ready')

    def OnDeInit(self):
        super().OnDeInit()
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
                    self.UpdateTrack(n)

    def OnMidiMsg(self, event):
        if (event.midiId == midi.MIDI_CONTROLCHANGE):
            if (event.midiChan == 0):
                event.inEv = event.data2
                if event.inEv >= 0x40:
                    event.outEv = -(event.inEv - 0x40)
                else:
                    event.outEv = event.inEv

                # knobs
                if event.data1 in [0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17]:
                    Res = 0.005 + ((abs(event.outEv)-1) / 2000)
                    if self.Page == mcu_pages.Free:
                        i = event.data1 - 0x10
                        event.data1 = self.Tracks[i].BaseEventID + int(self.Tracks[i].KnobHeld)
                        event.isIncrement = 1
                        s = chr(0x2B + int(event.outEv < 0)*2) # + or - sign depending on how you rotate
                        self.OnSendMsg('Free knob ' + str(event.data1) + ': ' + s + str(abs(event.outEv)))
                        device.processMIDICC(event)
                        device.hardwareRefreshMixerTrack(self.Tracks[i].TrackNum)
                    else:
                        super().SetKnobValue(event.data1 - 0x10, event.outEv, Res)
                        event.handled = True
                else:
                    event.handled = False # for extra CCs in emulators
            else:
                event.handled = False # for extra CCs in emulators

        elif event.midiId == midi.MIDI_PITCHBEND: # pitch bend (faders)

            if event.midiChan <= 8:
                event.inEv = event.data1 + (event.data2 << 7)
                event.outEv = (event.inEv << 16) // 16383
                event.inEv -= 0x2000

                if self.Page == mcu_pages.Free:
                    self.FreeCtrlT[self.Tracks[event.midiChan].TrackNum] = event.data1 + (event.data2 << 7)
                    device.hardwareRefreshMixerTrack(self.Tracks[event.midiChan].TrackNum)
                    event.data1 = self.Tracks[event.midiChan].BaseEventID + 7
                    event.midiChan = 0
                    event.midiChanEx = 0
                    self.OnSendMsg('Free slider ' + str(event.data1) + ': ' + ui.getHintValue(event.outEv, 65523))
                    event.status = event.midiId = midi.MIDI_CONTROLCHANGE
                    event.isIncrement = 0
                    event.outEv = int(event.data2 / 127.0 * midi.FromMIDI_Max)
                    device.processMIDICC(event)
                elif self.Tracks[event.midiChan].SliderEventID >= 0:
                    # slider (mixer track volume)
                    event.handled = True
                    mixer.automateEvent(self.Tracks[event.midiChan].SliderEventID, mcu_device_fader_conversion.McuFaderToFlFader(event.inEv + 0x2000), midi.REC_MIDIController, self.SmoothSpeed)
                    # hint
                    n = mixer.getAutoSmoothEventValue(self.Tracks[event.midiChan].SliderEventID)
                    s = mixer.getEventIDValueString(self.Tracks[event.midiChan].SliderEventID, n)
                    if s != '':
                        s = ': ' + s
                    self.OnSendMsg(self.Tracks[event.midiChan].SliderName + s)

        elif (event.midiId == midi.MIDI_NOTEON) | (event.midiId == midi.MIDI_NOTEOFF):  # NOTE
            if event.midiId == midi.MIDI_NOTEON:
                if (event.pmeFlags & midi.PME_FromScript != 0):
                    if event.data1 == 0x7F:
                        self.SetFirstTrack(event.data2)
                # slider hold
                if (event.data1 in [mcu_buttons.Slider_1, mcu_buttons.Slider_2, mcu_buttons.Slider_3, mcu_buttons.Slider_4, mcu_buttons.Slider_5, mcu_buttons.Slider_6, mcu_buttons.Slider_7, mcu_buttons.Slider_8, mcu_buttons.Slider_Main]):
                    # Auto select channel
                    if event.data1 != mcu_buttons.Slider_Main and event.data2 > 0 and (self.Page == mcu_pages.Pan or self.Page == mcu_pages.Stereo):
                        fader_index = event.data1 - mcu_buttons.Slider_1
                        if mixer.trackNumber != self.Tracks[fader_index].TrackNum:
                            mixer.setTrackNumber(self.Tracks[fader_index].TrackNum)
                    event.handled = True
                    return

                if (event.pmeFlags & midi.PME_System != 0):
                    if event.data1 == mcu_buttons.NameValue: # display mode
                        if event.data2 > 0:
                            pass #don't react, this button (name/value) can do other stuff now
                            #self.MeterMode = (self.MeterMode + 1) % 3
                            #self.OnSendMsg(self.MackieCU_MeterModeNameT[self.MeterMode])
                            #self.UpdateMeterMode()
                    elif (event.data1 == mcu_buttons.FaderBankLeft) | (event.data1 == mcu_buttons.FaderBankRight): # mixer bank
                        if event.data2 > 0:
                            self.SetFirstTrack(self.FirstTrackT[self.FirstTrack] - 8 + int(event.data1 == mcu_buttons.FaderBankRight) * 16)
                    elif (event.data1 == mcu_buttons.FaderChannelLeft) | (event.data1 == mcu_buttons.FaderChannelRight):
                        if event.data2 > 0:
                            self.SetFirstTrack(self.FirstTrackT[self.FirstTrack] - 1 + int(event.data1 == mcu_buttons.FaderChannelRight) * 2)
                    elif event.data1 == mcu_buttons.Flip: # self.Flip
                        if event.data2 > 0:
                            self.Flip = not self.Flip
                            self.UpdateColT()
                    elif event.data1 in [mcu_buttons.Encoder_1, mcu_buttons.Encoder_2, mcu_buttons.Encoder_3, mcu_buttons.Encoder_4, mcu_buttons.Encoder_5, mcu_buttons.Encoder_6, mcu_buttons.Encoder_7, mcu_buttons.Encoder_8]: # knob reset
                        if self.Page == mcu_pages.Free:
                            i = event.data1 - mcu_buttons.Encoder_1
                            self.Tracks[i].KnobHeld = event.data2 > 0
                            if event.data2 > 0:
                                event.data1 = self.Tracks[i].BaseEventID + 2
                                event.outEv = 0
                                event.isIncrement = 2
                                self.OnSendMsg('Free knob switch ' + str(event.data1))
                                device.processMIDICC(event)
                            device.hardwareRefreshMixerTrack(self.Tracks[i].TrackNum)
                            return
                        elif event.data2 > 0:
                            n = event.data1 - mcu_buttons.Encoder_1
                            if self.Page == mcu_pages.Sends:
                                if mixer.setRouteTo(mixer.trackNumber(), self.Tracks[n].TrackNum, -1) < 0:
                                    self.OnSendMsg('Cannot send to this track')
                                else:
                                    mixer.afterRoutingChanged()
                            else:
                                super().SetKnobValue(n, midi.MaxInt)

                    elif (event.data1 >= 0) & (event.data1 <= 0x1F): # free hold buttons
                        if self.Page == mcu_pages.Free:
                            i = event.data1 % 8
                            event.data1 = self.Tracks[i].BaseEventID + 3 + event.data1 // 8
                            event.inEv = event.data2
                            event.outEv = int(event.inEv > 0) * midi.FromMIDI_Max
                            self.OnSendMsg('Free button ' + str(event.data1) + ': ' + mcu_constants.OffOnStr[event.outEv > 0])
                            device.processMIDICC(event)
                            device.hardwareRefreshMixerTrack(self.Tracks[i].TrackNum)
                            return

                    elif event.data1 in [mcu_buttons.Pan, mcu_buttons.Sends, mcu_buttons.Equalizer, mcu_buttons.Stereo, mcu_buttons.Effects, mcu_buttons.Free]: # self.Page
                        if event.data2 > 0:
                            n = event.data1 - mcu_buttons.Pan
                            self.OnSendMsg(mcu_constants.PageDescriptions[n])
                            self.SetPage(n)
                            #device.dispatch(0, midi.MIDI_NOTEON + (event.data1 << 8) + (event.data2 << 16) )

                if (event.pmeFlags & midi.PME_System_Safe != 0):
                    if event.data1 == mcu_buttons.LinkChannel: # link selected channels to current mixer track
                        if event.data2 > 0:
                            if self.Shift:
                                mixer.linkTrackToChannel(midi.ROUTE_StartingFromThis)
                            else:
                                mixer.linkTrackToChannel(midi.ROUTE_ToThis)
                    elif (event.data1 >= mcu_buttons.Select_1) & (event.data1 <= mcu_buttons.Select_8): # select mixer track
                        if event.data2 > 0:
                            i = event.data1 - mcu_buttons.Select_1
                            ui.showWindow(midi.widMixer)
                            mixer.setTrackNumber(self.Tracks[i].TrackNum, midi.curfxScrollToMakeVisible | midi.curfxMinimalLatencyUpdate)

                    elif (event.data1 >= mcu_buttons.Solo_1) & (event.data1 <= mcu_buttons.Solo_8): # solo
                        if event.data2 > 0:
                            i = event.data1 - mcu_buttons.Solo_1
                            self.Tracks[i].solomode = midi.fxSoloModeWithDestTracks
                            if self.Shift:
                                pass #function does not exist: Include(self.Tracks[i].solomode, midi.fxSoloModeWithSourceTracks)
                            mixer.soloTrack(self.Tracks[i].TrackNum, midi.fxSoloToggle, self.Tracks[i].solomode)
                            mixer.setTrackNumber(self.Tracks[i].TrackNum, midi.curfxScrollToMakeVisible)

                    elif (event.data1 >= mcu_buttons.Mute_1) & (event.data1 <= mcu_buttons.Mute_8): # mute
                        if event.data2 > 0:
                            mixer.enableTrack(self.Tracks[event.data1 - mcu_buttons.Mute_1].TrackNum)

                    elif (event.data1 >= mcu_buttons.Record_1) & (event.data1 <= mcu_buttons.Record_8): # arm
                        if event.data2 > 0:
                            mixer.armTrack(self.Tracks[event.data1].TrackNum)
                            if mixer.isTrackArmed(self.Tracks[event.data1].TrackNum):
                                self.OnSendMsg(tracknames.GetAsciiSafeTrackName(self.Tracks[event.data1].TrackNum) + ' recording to ' + mixer.getTrackRecordingFileName(self.Tracks[event.data1].TrackNum))
                            else:
                                self.OnSendMsg(tracknames.GetAsciiSafeTrackName(self.Tracks[event.data1].TrackNum) + ' unarmed')

                    event.handled = True
                else:
                    event.handled = False
            else:
                event.handled = False

    def UpdateMsg(self):
        self.McuDevice.SetTextDisplay(self.MsgT[1])

    def OnSendMsg(self, Msg):
        super().OnSendMsg(Msg)

    def SetPage(self, Value):

        oldPage = self.Page
        self.Page = Value

        self.FirstTrack = int(self.Page == mcu_pages.Free)
        #if self.Page == oldPage:
        self.SetFirstTrack(self.FirstTrackT[self.FirstTrack])

        if self.Page == mcu_pages.Free:

            BaseID = midi.EncodeRemoteControlID(device.getPortNumber(), 0, mcu_constants.FreeEventID + 7)
            for n in range(0, len(self.FreeCtrlT)):
                d = mixer.remoteFindEventValue(BaseID + n * 8, 1)
                if d >= 0:
                    self.FreeCtrlT[n] = min(round(d * 16384), 16384)

        if (oldPage == mcu_pages.Free) | (self.Page == mcu_pages.Free):
            self.UpdateMeterMode()
        self.UpdateColT()
        self.UpdateTextDisplay()

    def UpdateMixer_Sel(self):
        if device.isAssigned():
            for m in range(0, len(self.Tracks) - 1):
                self.McuDevice.GetTrack(m).buttons.SetSelectButton(self.Tracks[m].TrackNum == mixer.trackNumber(), True)

    def SetFirstTrack(self, Value):
        self.FirstTrackT[self.FirstTrack] = (Value + mixer.trackCount()) % mixer.trackCount()
        self.UpdateColT()
        device.hardwareRefreshMixerTrack(-1)

MackieCU_Ext = TMackieCU_Ext()

def OnInit():
    MackieCU_Ext.OnInit()

def OnDeInit():
    MackieCU_Ext.OnDeInit()

def OnDirtyMixerTrack(SetTrackNum):
    MackieCU_Ext.OnDirtyMixerTrack(SetTrackNum)

def OnRefresh(Flags):
    MackieCU_Ext.OnRefresh(Flags)

def OnMidiMsg(event):
    MackieCU_Ext.OnMidiMsg(event)

def OnSendTempMsg(Msg, Duration = 1000):
    MackieCU_Ext.OnSendMsg(Msg)

def OnUpdateMeters():
    MackieCU_Ext.OnUpdateMeters()

def OnIdle():
    MackieCU_Ext.OnIdle()
