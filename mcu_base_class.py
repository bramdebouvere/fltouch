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
import mcu_knob


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
                s = mixer.getTrackName(self.Tracks[m].TrackNum, 7)
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

    def UpdateTrack(self, Num):
        """ Updates the sliders, buttons & rotary encoders for a specific track """
        data1 = 0
        baseID = 0
        center = 0

        if device.isAssigned():
            if self.Page == mcu_pages.Free:
                baseID = midi.EncodeRemoteControlID(device.getPortNumber(), 0, self.Tracks[Num].BaseEventID)
                # slider
                m = self.FreeCtrlT[self.Tracks[Num].TrackNum]
                self.McuDevice.GetTrack(Num).fader.SetLevel(m, True)
                if Num < 8:
                    # ring
                    d = mixer.remoteFindEventValue(baseID + int(self.Tracks[Num].KnobHeld))
                    if d >= 0:
                        m = 1 + round(d * 10)
                    else:
                        m = int(self.Tracks[Num].KnobHeld) * (11 + (2 << 4))
                    device.midiOutNewMsg(midi.MIDI_CONTROLCHANGE + ((0x30 + Num) << 8) + (m << 16), self.Tracks[Num].LastValueIndex)
                    # buttons
                    buttonActive = False
                    for buttonIndex in range(0, 4):
                        d = mixer.remoteFindEventValue(baseID + 3 + buttonIndex)
                        if d >= 0:
                            buttonActive = d >= 0.5
                        else:
                            buttonActive = False

                        self.McuDevice.GetTrack(Num).buttons.SetButtonByIndex(buttonIndex, buttonActive, True)
            else:
                sv = mixer.getEventValue(self.Tracks[Num].SliderEventID)

                if Num < 8:
                    # V-Pot
                    center = self.Tracks[Num].KnobCenter
                    knobMode = self.Tracks[Num].KnobMode

                    if self.Tracks[Num].KnobEventID >= 0:
                        m = mixer.getEventValue(self.Tracks[Num].KnobEventID, midi.MaxInt, False)
                        if center < 0:
                            if self.Tracks[Num].KnobResetEventID == self.Tracks[Num].KnobEventID:
                                center = int(m !=  self.Tracks[Num].KnobResetValue)
                            else:
                                center = int(sv !=  self.Tracks[Num].KnobResetValue)

                        if knobMode == mcu_knob.Parameter or knobMode == mcu_knob.Pan:
                            data1 = 1 + round(m * (10 / midi.FromMIDI_Max)) + (center << 6) + (knobMode << 4)
                        elif knobMode == mcu_knob.Volume:
                            data1 = round(m * (11 / midi.FromMIDI_Max)) + (center << 6) + (knobMode << 4)
                        elif knobMode == mcu_knob.Off:
                            data1 = (center << 6)
                        else:
                            print('Unsupported knob mode')
                    else:
                        data1 = 0

                    device.midiOutNewMsg(midi.MIDI_CONTROLCHANGE + ((0x30 + Num) << 8) + (data1 << 16), self.Tracks[Num].LastValueIndex)

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
        if not (self.Tracks[trackNumber].KnobEventID >= 0) & (self.Tracks[trackNumber].KnobMode != mcu_knob.Off):
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

