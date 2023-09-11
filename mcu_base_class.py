import device
import ui
import time
import utils
import mixer
import midi
import transport
import general
import channels

import mcu_constants
import mcu_device
import mcu_track
import mcu_pages
import mcu_knob_mode
import tracknames

class McuBaseClass():
    """ Shared base class for both the extender and the main mackie unit """

    def __init__(self, device: mcu_device.McuDevice):
        self.MsgT = ["", ""]
        self.Tracks = [mcu_track.McuTrack() for i in range(0)] # empty array, since "import typing" is not supported

        self.Shift = False # indicates that the shift button is pressed
        self.MsgDirty = False

        self.FirstTrack = 0 # the count mode for the tracks (0 = normal, 1 = free mode)
        self.FirstTrackT = [0, 0]

        self.FreeCtrlT = [0 for x in range(mcu_constants.FreeTrackCount + 1)]  # 64+1 sliders
        self.Clicking = False

        self.Page = 0
        self.Flip = False
        
        self.SmoothSpeed = 0

        self.McuDevice = device

    def OnInit(self):
        """ Called when the script has been started """
        self.FirstTrackT[0] = 1
        self.FirstTrack = 0
        self.SmoothSpeed = 0 # TODO: is not required if OnInit is not called more than once, need to check if this is the case
        self.Clicking = True

        device.setHasMeters()
        
        # set free mode faders to center
        for m in range(0, len(self.FreeCtrlT)):
            self.FreeCtrlT[m] = 8192 

        # init hardware
        self.McuDevice.Initialize()
        self.McuDevice.SetBackLightTimeout(2) # backlight timeout to 2 minutes
        self.McuDevice.SetClicking(self.Clicking)

    def OnDeInit(self):
        """ Called before the script will be stopped """
        self.McuDevice.DisableMeters()

        if device.isAssigned():
            if ui.isClosing():
                self.McuDevice.SetTextDisplay(ui.getProgTitle() + ' session closed at ' + time.ctime(time.time()), 0, skipIsAssignedCheck = True)
            else:
                self.McuDevice.SetTextDisplay('', skipIsAssignedCheck = True)

            self.McuDevice.SetTextDisplay('', 1, skipIsAssignedCheck = True)
            self.McuDevice.SetScreenColors(skipIsAssignedCheck = True)

    def OnDirtyMixerTrack(self, SetTrackNum):
        """
        Called on mixer track(s) change, 'SetTrackNum' indicates track index of track that changed or -1 when all tracks changed
        collect info about 'dirty' tracks here but do not handle track(s) refresh, wait for OnRefresh event with HW_Dirty_Mixer_Controls flag
        """
        for m in range(0, len(self.Tracks)):
            if (self.Tracks[m].TrackNum == SetTrackNum) | (SetTrackNum == -1):
                self.Tracks[m].Dirty = True

    def UpdateTextDisplay(self):
        """ Updates the mixer track names and colors """
        # Update names
        s1 = ''
        for m in range(0, len(self.Tracks) - 1):
            s = ''
            if self.Page == mcu_pages.Free:
                s = '  ' + utils.Zeros(self.Tracks[m].TrackNum + 1, 2, ' ')
            else:
                s = tracknames.GetAsciiSafeTrackName(self.Tracks[m].TrackNum, 7)
            for n in range(1, 7 - len(s) + 1):
                s = s + ' '
            s1 = s1 + s

        self.McuDevice.SetTextDisplay(s1, 1)

        # Update colors
        if self.Page == mcu_pages.Free:
            self.McuDevice.SetScreenColors() # all white
        else:
            colorArr = []
            for m in range(0, len(self.Tracks) - 1):
                c = mixer.getTrackColor(self.Tracks[m].TrackNum)
                colorArr.append(c)
            self.McuDevice.SetScreenColors(colorArr)

    def UpdateMeterMode(self):
        self.McuDevice.ClearMeters()
        self.McuDevice.DisableMeters() #TODO: check if it's actually required to disable and then enable again here

        # reset stuff
        self.UpdateTextDisplay()
        self.McuDevice.EnableMeters()

    def OnUpdateMeters(self):
        """ Called when peak meters have updated values """
        if self.Page != mcu_pages.Free:
            for track in self.McuDevice.tracksWithMeters:
                currentPeak = mixer.getTrackPeaks(self.Tracks[track.index].TrackNum, midi.PEAK_LR_INV)
                track.meter.SetValue(currentPeak)

    def OnIdle(self):
        """ Called from time to time. Can be used to do some small tasks, mostly UI related """
        # temp message
        if self.MsgDirty:
            self.UpdateMsg()
            self.MsgDirty = False

    def UpdateColT(self):
        firstTrackNum = self.FirstTrackT[self.FirstTrack]
        CurID = mixer.getTrackPluginId(mixer.trackNumber(), 0)

        for i in range(0, len(self.Tracks)):
            if self.Page == mcu_pages.Free:
                # free controls
                if i == 8:
                    self.Tracks[i].TrackNum = mcu_constants.FreeTrackCount
                else:
                    self.Tracks[i].TrackNum = (firstTrackNum + i) % mcu_constants.FreeTrackCount

                self.Tracks[i].KnobName = 'Knob ' + str(self.Tracks[i].TrackNum + 1)
                self.Tracks[i].SliderName = 'Slider ' + str(self.Tracks[i].TrackNum + 1)

                self.Tracks[i].BaseEventID = mcu_constants.FreeEventID + self.Tracks[i].TrackNum * 8 # first virtual CC
            else:
                self.Tracks[i].KnobPressEventID = -1

                # mixer
                if i == 8:
                    self.Tracks[i].TrackNum = -2
                    self.Tracks[i].BaseEventID = midi.REC_MainVol
                    self.Tracks[i].SliderEventID = self.Tracks[i].BaseEventID
                    self.Tracks[i].SliderName = 'Master Vol'
                else:
                    self.Tracks[i].TrackNum = midi.TrackNum_Master + ((firstTrackNum + i) % mixer.trackCount())
                    self.Tracks[i].BaseEventID = mixer.getTrackPluginId(self.Tracks[i].TrackNum, 0)
                    self.Tracks[i].SliderEventID = self.Tracks[i].BaseEventID + midi.REC_Mixer_Vol
                    s = tracknames.GetAsciiSafeTrackName(self.Tracks[i].TrackNum)
                    self.Tracks[i].SliderName = s + ' - Vol'

                    self.Tracks[i].KnobEventID = -1
                    self.Tracks[i].KnobResetEventID = -1
                    self.Tracks[i].KnobResetValue = midi.FromMIDI_Max >> 1
                    self.Tracks[i].KnobName = ''
                    self.Tracks[i].KnobMode = mcu_knob_mode.BoostCut # parameter, pan, volume, off
                    self.Tracks[i].KnobCenter = -1

                    if self.Page == mcu_pages.Pan:
                        self.Tracks[i].KnobEventID = self.Tracks[i].BaseEventID + midi.REC_Mixer_Pan
                        self.Tracks[i].KnobResetEventID = self.Tracks[i].KnobEventID
                        self.Tracks[i].KnobName = tracknames.GetAsciiSafeTrackName(self.Tracks[i].TrackNum) + ' - ' + 'Pan'
                    elif self.Page == mcu_pages.Stereo:
                        self.Tracks[i].KnobEventID = self.Tracks[i].BaseEventID + midi.REC_Mixer_SS
                        self.Tracks[i].KnobResetEventID = self.Tracks[i].KnobEventID
                        self.Tracks[i].KnobName = tracknames.GetAsciiSafeTrackName(self.Tracks[i].TrackNum) + ' - ' + 'Sep'
                    elif self.Page == mcu_pages.Sends:
                        self.Tracks[i].KnobEventID = CurID + midi.REC_Mixer_Send_First + self.Tracks[i].TrackNum
                        s = mixer.getEventIDName(self.Tracks[i].KnobEventID)
                        self.Tracks[i].KnobName = s
                        self.Tracks[i].KnobResetValue = round(12800 * midi.FromMIDI_Max / 16000)
                        self.Tracks[i].KnobCenter = mixer.getRouteSendActive(mixer.trackNumber(),self.Tracks[i].TrackNum)
                        if self.Tracks[i].KnobCenter == 0:
                            self.Tracks[i].KnobMode = mcu_knob_mode.Off
                        else:
                            self.Tracks[i].KnobMode = mcu_knob_mode.Wrap
                    elif self.Page == mcu_pages.Effects:
                        CurID = mixer.getTrackPluginId(mixer.trackNumber(), i)
                        self.Tracks[i].KnobEventID = CurID + midi.REC_Plug_MixLevel
                        s = mixer.getEventIDName(self.Tracks[i].KnobEventID)
                        self.Tracks[i].KnobName = s
                        self.Tracks[i].KnobResetValue = midi.FromMIDI_Max

                        IsValid = mixer.isTrackPluginValid(mixer.trackNumber(), i)
                        IsEnabledAuto = mixer.isTrackAutomationEnabled(mixer.trackNumber(), i)
                        if IsValid:
                            self.Tracks[i].KnobMode = mcu_knob_mode.Wrap
                            self.Tracks[i].KnobPressEventID = CurID + midi.REC_Plug_Mute
                        else:
                            self.Tracks[i].KnobMode = mcu_knob_mode.Off
                        self.Tracks[i].KnobCenter = int(IsValid & IsEnabledAuto)
                    elif self.Page == mcu_pages.Equalizer:
                        if self.McuDevice.isExtender or i >= 6:
                            # disable encoders on extenders and tracks > 6
                            self.Tracks[i].SliderEventID = -1
                            self.Tracks[i].KnobEventID = -1
                            self.Tracks[i].KnobMode = mcu_knob_mode.Off
                        elif i < 3:
                            # gain & freq
                            self.Tracks[i].SliderEventID = CurID + midi.REC_Mixer_EQ_Gain + i
                            self.Tracks[i].KnobResetEventID = self.Tracks[i].SliderEventID
                            s = mixer.getEventIDName(self.Tracks[i].SliderEventID)
                            self.Tracks[i].SliderName = s
                            self.Tracks[i].KnobEventID = CurID + midi.REC_Mixer_EQ_Freq + i
                            s = mixer.getEventIDName(self.Tracks[i].KnobEventID)
                            self.Tracks[i].KnobName = s
                            self.Tracks[i].KnobResetValue = midi.FromMIDI_Max >> 1
                            self.Tracks[i].KnobCenter = -2
                            self.Tracks[i].KnobMode = mcu_knob_mode.SingleDot
                        else:
                            # Q
                            self.Tracks[i].SliderEventID = CurID + midi.REC_Mixer_EQ_Q + i - 3
                            self.Tracks[i].KnobResetEventID = self.Tracks[i].SliderEventID
                            s = mixer.getEventIDName(self.Tracks[i].SliderEventID)
                            self.Tracks[i].SliderName = s
                            self.Tracks[i].KnobEventID = self.Tracks[i].SliderEventID
                            self.Tracks[i].KnobName = self.Tracks[i].SliderName
                            self.Tracks[i].KnobResetValue = 17500
                            self.Tracks[i].KnobCenter = -1
                            self.Tracks[i].KnobMode = mcu_knob_mode.Wrap

                    # self.Flip knob & slider
                    if self.Flip:
                        self.Tracks[i].KnobEventID, self.Tracks[i].SliderEventID = utils.SwapInt(self.Tracks[i].KnobEventID, self.Tracks[i].SliderEventID)
                        s = self.Tracks[i].SliderName
                        self.Tracks[i].SliderName = self.Tracks[i].KnobName
                        self.Tracks[i].KnobName = s
                        self.Tracks[i].KnobMode = mcu_knob_mode.Wrap
                        if not (self.Page in [mcu_pages.Sends, mcu_pages.Effects, mcu_pages.Equalizer if self.McuDevice.isExtender else -1 ]):
                            self.Tracks[i].KnobCenter = -1
                            self.Tracks[i].KnobResetValue = round(12800 * midi.FromMIDI_Max / 16000)
                            self.Tracks[i].KnobResetEventID = self.Tracks[i].KnobEventID

            self.UpdateTrack(i)

    def UpdateTrack(self, Num):
        """ Updates the sliders, buttons & rotary encoders for a specific track """

        # do not process tracks above 8 on extenders
        if self.McuDevice.isExtender and Num >= 8:
            return

        if device.isAssigned():
            if self.Page == mcu_pages.Free:
                baseID = midi.EncodeRemoteControlID(device.getPortNumber(), 0, self.Tracks[Num].BaseEventID)

                # slider
                sliderValue = self.FreeCtrlT[self.Tracks[Num].TrackNum]
                self.McuDevice.GetTrack(Num).fader.SetLevel(sliderValue, True)

                #encoder knobs
                if Num < 8:
                    # ring
                    d = mixer.remoteFindEventValue(baseID + int(self.Tracks[Num].KnobHeld)) # float 0.0-1.0 
                    if d >= 0:
                        value = 1 + round(d * 10) # 1-11
                        self.McuDevice.GetTrack(Num).knob.setLedsValue(mcu_knob_mode.SingleDot, False, value)
                    else:
                        if self.Tracks[Num].KnobHeld:
                            self.McuDevice.GetTrack(Num).knob.setLedsValueAll()
                        else:
                            self.McuDevice.GetTrack(Num).knob.SetLedsValueNone()
                    
                    # buttons
                    for buttonIndex in range(0, 4):
                        d = mixer.remoteFindEventValue(baseID + 3 + buttonIndex)
                        buttonActive = d >= 0.5 if d >= 0 else False

                        self.McuDevice.GetTrack(Num).buttons.SetButtonByIndex(buttonIndex, buttonActive, True)
            else:
                sv = mixer.getEventValue(self.Tracks[Num].SliderEventID)

                if Num < 8:
                    # V-Pot
                    center = self.Tracks[Num].KnobCenter
                    knobMode = self.Tracks[Num].KnobMode
                    value = 0

                    if self.Tracks[Num].KnobEventID >= 0:
                        m = mixer.getEventValue(self.Tracks[Num].KnobEventID, midi.MaxInt, False)
                        if center < 0:
                            if self.Tracks[Num].KnobResetEventID == self.Tracks[Num].KnobEventID:
                                center = int(m != self.Tracks[Num].KnobResetValue)
                            else:
                                center = int(sv != self.Tracks[Num].KnobResetValue)

                        if knobMode == mcu_knob_mode.SingleDot or knobMode == mcu_knob_mode.BoostCut:
                            value = 1 + round(m * (10 / midi.FromMIDI_Max))
                        elif knobMode == mcu_knob_mode.Wrap:
                            value = round(m * (11 / midi.FromMIDI_Max))
                        else:
                            print('Unsupported knob mode')

                    # device.midiOutNewMsg(midi.MIDI_CONTROLCHANGE + ((0x30 + Num) << 8) + (data1 << 16), self.Tracks[Num].LastValueIndex)

                    self.McuDevice.GetTrack(Num).knob.setLedsValue(knobMode, center, value)


                    # arm, solo, mute
                    self.McuDevice.GetTrack(Num).buttons.SetArmButton(mixer.isTrackArmed(self.Tracks[Num].TrackNum), transport.isRecording(), True)
                    self.McuDevice.GetTrack(Num).buttons.SetSoloButton(mixer.isTrackSolo(self.Tracks[Num].TrackNum), True)
                    self.McuDevice.GetTrack(Num).buttons.SetMuteButton(not mixer.isTrackEnabled(self.Tracks[Num].TrackNum), True)

                # slider
                self.McuDevice.GetTrack(Num).fader.SetLevelFromFlsFader(sv, True)

            self.Tracks[Num].Dirty = False

    def OnSendMsg(self, Msg):
        self.MsgT[1] = Msg
        self.MsgDirty = True

    def SetKnobValue(self, trackNumber, midiValue, resolution = midi.EKRes):
        """ Sets the value of a knob in FL Studio (for all except free page?) (and shows it on the display) """
        if not (self.Tracks[trackNumber].KnobEventID >= 0) & (self.Tracks[trackNumber].KnobMode != mcu_knob_mode.Off):
            return

        if midiValue == midi.MaxInt:
            if self.Page == mcu_pages.Effects:
                if self.Tracks[trackNumber].KnobPressEventID >= 0:
                    midiValue = channels.incEventValue(self.Tracks[trackNumber].KnobPressEventID, 0, midi.EKRes)
                    general.processRECEvent(self.Tracks[trackNumber].KnobPressEventID, midiValue, midi.REC_Controller)
                    s = mixer.getEventIDName(self.Tracks[trackNumber].KnobPressEventID)
                    self.OnSendMsg(s)
                return
            else:
                mixer.automateEvent(self.Tracks[trackNumber].KnobResetEventID, self.Tracks[trackNumber].KnobResetValue, midi.REC_MIDIController, self.SmoothSpeed)
        else:
            mixer.automateEvent(self.Tracks[trackNumber].KnobEventID, midiValue, midi.REC_Controller, self.SmoothSpeed, 1, resolution)

        # show the value of the knob on the display
        n = mixer.getAutoSmoothEventValue(self.Tracks[trackNumber].KnobEventID)
        s = mixer.getEventIDValueString(self.Tracks[trackNumber].KnobEventID, n)
        if s !=  '':
            s = ': ' + s
        self.OnSendMsg(self.Tracks[trackNumber].KnobName + s)

