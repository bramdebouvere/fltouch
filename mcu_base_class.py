import device
import ui
import time
import utils
import mixer
import midi
import transport
import general
import channels

from behaviors.mcu_base_behavior import McuBaseBehavior
from behaviors.track_banking_behavior import TrackBankingBehavior
from device_hal import mcu_buttons
from utilities.track_banking_manager import TrackBankingManager
import constants.mcu_constants as mcu_constants
from constants import eq_controls
from device_hal.mcu_device import McuDevice
from mcu_track import McuTrack
import constants.mcu_modes as mcu_modes
import device_hal.mcu_knob_mode as mcu_knob_mode
from modes.mcu_base_mode import McuBaseMode
from modes.mcu_effects_mode import McuEffectsMode
from modes.mcu_effects_mode import McuEffectsMode
from modes.mcu_eq_mode import McuEQMode
from modes.mcu_pan_mode import McuPanMode
from modes.mcu_sends_mode import McuSendsMode
from modes.mcu_stereo_mode import McuStereoMode
from modes.mcu_unused_mode import McuUnusedMode
from modes.mcu_unused_mode import McuUnusedMode
import utilities.transliteration as transliteration

class McuBaseClass():
    """ Shared base class for both the extender and the main mackie unit """

    def __init__(self, device: McuDevice):
        self.McuDevice = device

        # create track banking managers
        self.mixerTrackManager = TrackBankingManager(self.McuDevice)
        self.effectsSlotTrackManager = TrackBankingManager(self.McuDevice, mcu_constants.EffectsSlotCount) # banks the 10 effect slots of the selected track (Effects mode, slot overview)
        self.effectsParamTrackManager = TrackBankingManager(self.McuDevice, 0) # banks the focused plugin's parameters (Effects mode, parameter view); count is set at runtime
        self.eqTrackManager = TrackBankingManager(self.McuDevice, eq_controls.EqControlCount) # banks the 9 EQ controls of the selected track

        # create modes
        self.modes: dict[int, McuBaseMode] = {
            mcu_modes.Pan: McuPanMode(self.McuDevice, self.mixerTrackManager),
            mcu_modes.Sends: McuSendsMode(self.McuDevice, self.mixerTrackManager),
            mcu_modes.Equalizer: McuEQMode(self.McuDevice, self.eqTrackManager),
            mcu_modes.Stereo: McuStereoMode(self.McuDevice, self.mixerTrackManager),
            mcu_modes.Effects: McuEffectsMode(self.McuDevice, self.effectsSlotTrackManager, self.effectsParamTrackManager),
            mcu_modes.Free: McuUnusedMode(self.McuDevice, self.mixerTrackManager)
        }

        self.Mode: McuBaseMode | None = None # the current mode

        self.PermanentBehaviors = [McuBaseBehavior(device) for i in range(0)] # empty array, since "import typing" is not supported

        self.Tracks = [McuTrack() for i in range(0)] # empty array, since "import typing" is not supported

        self.Shift = False # indicates that the shift button is pressed
        self.MsgDirty = False

        self.FirstTrack = 0 # the count mode for the tracks (0 = normal, 1 = free mode)
        self.FirstTrackT = [0, 0]

        self.FreeCtrlT = [0 for x in range(mcu_constants.FreeTrackCount + 1)]  # 64+1 sliders

        self.Flip = False



    def EnableMode(self, mode: McuBaseMode):
        """ Changes the currently active mode to another mode """
        if (self.Mode == mode):
            return
        if (self.Mode != None):
            self.Mode.OnDisable()
        self.Mode = mode
        self.Mode.OnEnable()

    def OnInit(self):
        """ Called when the script has been started """
        for behavior in self.PermanentBehaviors:
            behavior.OnEnable()

        #self.FirstTrackT[0] = 1
        #self.FirstTrack = 0

        #device.setHasMeters()
        
        # set free mode faders to center
        #for m in range(0, len(self.FreeCtrlT)):
        #    self.FreeCtrlT[m] = 8192 

        # init hardware
        self.McuDevice.Initialize()
        self.McuDevice.SetBackLightTimeout(2) # backlight timeout to 2 minutes
        self.McuDevice.SetClicking(True)

        self.OnSendMsg('Linked to ' + ui.getProgTitle() + ' (' + ui.getVersion() + ')', 3000)
        print('OnInit ready')

    def OnDeInit(self):
        """ Called before the script will be stopped """
        for behavior in self.PermanentBehaviors:
            behavior.OnDisable()

        # if self.Mode != None:
        #     self.Mode.OnDisable()
        #     self.Mode = None
        
        #self.McuDevice.DisableMeters()

        #if device.isAssigned():
        #    if ui.isClosing():
        #        self.McuDevice.SetTextDisplay(ui.getProgTitle() + ' session closed at ' + time.ctime(time.time()), 0, skipIsAssignedCheck = True)
        #    else:
        #        self.McuDevice.SetTextDisplay('', skipIsAssignedCheck = True)
#
        #    self.McuDevice.SetTextDisplay('', 1, skipIsAssignedCheck = True)
        #    self.McuDevice.SetScreenColors(skipIsAssignedCheck = True)

    def OnDirtyMixerTrack(self, SetTrackNum):
        """
        Called on mixer track(s) change, 'SetTrackNum' indicates track index of track that changed or -1 when all tracks changed
        collect info about 'dirty' tracks here but do not handle track(s) refresh, wait for OnRefresh event with HW_Dirty_Mixer_Controls flag
        """
        for behavior in self.PermanentBehaviors:
            behavior.OnDirtyMixerTrack(SetTrackNum)
        if (self.Mode != None):
            self.Mode.OnDirtyMixerTrack(SetTrackNum)

    def UpdateTextDisplay(self):
        """ Updates the mixer track names and colors """
        pass
        # Update names
        #s1 = ''
        #for m in range(0, len(self.Tracks) - 1):
        #    s = ''
        #    if self.Mode == mcu_modes.Free:
        #        s = '  ' + utils.Zeros(self.Tracks[m].TrackNum + 1, 2, ' ')
        #    else:
        #        s = transliteration.GetAsciiSafeTrackName(self.Tracks[m].TrackNum, 7)
        #    for n in range(1, 7 - len(s) + 1):
        #        s = s + ' '
        #    s1 = s1 + s

        #self.McuDevice.SetTextDisplay(s1, 1)

        # Update colors
        #if self.Mode == mcu_modes.Free:
        #    self.McuDevice.SetScreenColors() # all white
        #else:
        #    colorArr = []
        #    for m in range(0, len(self.Tracks) - 1):
        #        c = mixer.getTrackColor(self.Tracks[m].TrackNum)
        #        colorArr.append(c)
        #    self.McuDevice.SetScreenColors(colorArr)

    def OnUpdateMeters(self):
        """ Called when peak meters have updated values """
        for behavior in self.PermanentBehaviors:
            behavior.OnUpdateMeters()
        if (self.Mode != None):
            self.Mode.OnUpdateMeters()
        
        #if self.Mode != mcu_modes.Free:
        #    for track in self.McuDevice.tracksWithMeters:
        #        assert track.meter is not None
        #        currentPeak = mixer.getTrackPeaks(self.Tracks[track.index].TrackNum, midi.PEAK_LR_INV)
        #        track.meter.SetValue(currentPeak)

    def OnIdle(self):
        """ Called from time to time. Can be used to do some small tasks, mostly UI related """
        for behavior in self.PermanentBehaviors:
            behavior.OnIdle()
        if (self.Mode != None):
            self.Mode.OnIdle()

    def UpdateColT(self):
        return # this code is now disabled, only kept for reference purposes (we are in a refactor and this will be removed later)
        firstTrackNum = self.FirstTrackT[self.FirstTrack]
        CurID = mixer.getTrackPluginId(mixer.trackNumber(), 0)

        for i in range(0, len(self.Tracks)):
            if self.Mode == mcu_modes.Free:
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
                    self.Tracks[i].SliderEventID = self.Tracks[i].BaseEventID + midi.REC_Mixer_Vol # type: ignore
                    s = transliteration.GetAsciiSafeTrackName(self.Tracks[i].TrackNum)
                    self.Tracks[i].SliderName = s + ' - Vol'

                    self.Tracks[i].KnobEventID = -1
                    self.Tracks[i].KnobResetEventID = -1
                    self.Tracks[i].KnobResetValue = midi.FromMIDI_Max >> 1
                    self.Tracks[i].KnobName = ''
                    self.Tracks[i].KnobMode = mcu_knob_mode.BoostCut # parameter, pan, volume, off
                    self.Tracks[i].KnobCenter = -1

                    if self.Mode == mcu_modes.Pan:
                        self.Tracks[i].KnobEventID = self.Tracks[i].BaseEventID + midi.REC_Mixer_Pan # type: ignore
                        self.Tracks[i].KnobResetEventID = self.Tracks[i].KnobEventID
                        self.Tracks[i].KnobName = transliteration.GetAsciiSafeTrackName(self.Tracks[i].TrackNum) + ' - ' + 'Pan'
                    elif self.Mode == mcu_modes.Stereo:
                        self.Tracks[i].KnobEventID = self.Tracks[i].BaseEventID + midi.REC_Mixer_SS # type: ignore
                        self.Tracks[i].KnobResetEventID = self.Tracks[i].KnobEventID
                        self.Tracks[i].KnobName = transliteration.GetAsciiSafeTrackName(self.Tracks[i].TrackNum) + ' - ' + 'Sep'
                    elif self.Mode == mcu_modes.Sends:
                        self.Tracks[i].KnobEventID = CurID + midi.REC_Mixer_Send_First + self.Tracks[i].TrackNum # type: ignore
                        s = mixer.getEventIDName(self.Tracks[i].KnobEventID)
                        self.Tracks[i].KnobName = s
                        self.Tracks[i].KnobResetValue = round(12800 * midi.FromMIDI_Max / 16000)
                        self.Tracks[i].KnobCenter = mixer.getRouteSendActive(mixer.trackNumber(),self.Tracks[i].TrackNum)
                        if self.Tracks[i].KnobCenter == 0:
                            self.Tracks[i].KnobMode = mcu_knob_mode.Off
                        else:
                            self.Tracks[i].KnobMode = mcu_knob_mode.Wrap
                    elif self.Mode == mcu_modes.Effects:
                        CurID = mixer.getTrackPluginId(mixer.trackNumber(), i)
                        self.Tracks[i].KnobEventID = CurID + midi.REC_Plug_MixLevel # type: ignore
                        s = mixer.getEventIDName(self.Tracks[i].KnobEventID)
                        self.Tracks[i].KnobName = s
                        self.Tracks[i].KnobResetValue = midi.FromMIDI_Max

                        IsValid = mixer.isTrackPluginValid(mixer.trackNumber(), i)
                        IsEnabledAuto = mixer.isTrackAutomationEnabled(mixer.trackNumber(), i)
                        if IsValid:
                            self.Tracks[i].KnobMode = mcu_knob_mode.Wrap
                            self.Tracks[i].KnobPressEventID = CurID + midi.REC_Plug_Mute # type: ignore
                        else:
                            self.Tracks[i].KnobMode = mcu_knob_mode.Off
                        self.Tracks[i].KnobCenter = int(IsValid & IsEnabledAuto)
                    elif self.Mode == mcu_modes.Equalizer:
                        if self.McuDevice.isExtender or i >= 6:
                            # disable encoders on extenders and tracks > 6
                            self.Tracks[i].SliderEventID = -1
                            self.Tracks[i].KnobEventID = -1
                            self.Tracks[i].KnobMode = mcu_knob_mode.Off
                        elif i < 3:
                            # gain & freq
                            self.Tracks[i].SliderEventID = CurID + midi.REC_Mixer_EQ_Gain + i # type: ignore
                            self.Tracks[i].KnobResetEventID = self.Tracks[i].SliderEventID
                            s = mixer.getEventIDName(self.Tracks[i].SliderEventID)
                            self.Tracks[i].SliderName = s
                            self.Tracks[i].KnobEventID = CurID + midi.REC_Mixer_EQ_Freq + i # type: ignore
                            s = mixer.getEventIDName(self.Tracks[i].KnobEventID)
                            self.Tracks[i].KnobName = s
                            self.Tracks[i].KnobResetValue = midi.FromMIDI_Max >> 1
                            self.Tracks[i].KnobCenter = -2
                            self.Tracks[i].KnobMode = mcu_knob_mode.SingleDot
                        else:
                            # Q
                            self.Tracks[i].SliderEventID = CurID + midi.REC_Mixer_EQ_Q + i - 3 # type: ignore
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
                        if not (self.Mode in [mcu_modes.Sends, mcu_modes.Effects, mcu_modes.Equalizer if self.McuDevice.isExtender else -1 ]):
                            self.Tracks[i].KnobCenter = -1
                            self.Tracks[i].KnobResetValue = round(12800 * midi.FromMIDI_Max / 16000)
                            self.Tracks[i].KnobResetEventID = self.Tracks[i].KnobEventID

            self.UpdateTrack(i)

    def UpdateTrack(self, Num):
        """ Updates the sliders, buttons & rotary encoders for a specific track """
        return # this code is now disabled, only kept for reference purposes (we are in a refactor and this will be removed later)

        # do not process tracks above 8 on extenders
        if self.McuDevice.isExtender and Num >= 8:
            return

        if device.isAssigned():
            if self.Mode == mcu_modes.Free:
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

    def OnSendMsg(self, Msg: str, duration: int = 2000):
        for behavior in self.PermanentBehaviors:
            behavior.OnSendTempMsg(Msg, duration)
        if (self.Mode != None):
            self.Mode.OnSendTempMsg(Msg, duration)

    def SetKnobValue(self, trackNumber, midiValue, resolution = midi.EKRes):
        """ Sets the value of a knob in FL Studio (for all except free page?) (and shows it on the display) """
        return # this code is now disabled, only kept for reference purposes (we are in a refactor and this will be removed later)
        if not (self.Tracks[trackNumber].KnobEventID >= 0) & (self.Tracks[trackNumber].KnobMode != mcu_knob_mode.Off):
            return

        if midiValue == midi.MaxInt:
            if self.Mode == mcu_modes.Effects:
                if self.Tracks[trackNumber].KnobPressEventID >= 0:
                    midiValue = channels.incEventValue(self.Tracks[trackNumber].KnobPressEventID, 0, midi.EKRes)
                    general.processRECEvent(self.Tracks[trackNumber].KnobPressEventID, midiValue, midi.REC_Controller)
                    s = mixer.getEventIDName(self.Tracks[trackNumber].KnobPressEventID)
                    self.OnSendMsg(s)
                return
            else:
                mixer.automateEvent(self.Tracks[trackNumber].KnobResetEventID, self.Tracks[trackNumber].KnobResetValue, midi.REC_MIDIController, 0)
        else:
            mixer.automateEvent(self.Tracks[trackNumber].KnobEventID, midiValue, midi.REC_Controller, 0, 1, resolution)

        # show the value of the knob on the display
        n = mixer.getAutoSmoothEventValue(self.Tracks[trackNumber].KnobEventID)
        s = mixer.getEventIDValueString(self.Tracks[trackNumber].KnobEventID, n)
        if s !=  '':
            s = ': ' + s
        self.OnSendMsg(self.Tracks[trackNumber].KnobName + s)

    def OnRefresh(self, flags):
        """ Called when certain events occur within FL Studio. Scripts should use the provided flags to update required interfaces on their associated controllers."""
        for behavior in self.PermanentBehaviors:
            behavior.OnRefresh(flags)
        if (self.Mode != None):
            self.Mode.OnRefresh(flags)

    def OnMidiMsg(self, event):
        """ Called when a MIDI message has been received """
        # check for mode change buttons
        if event.midiId == midi.MIDI_NOTEON:
            if event.data1 in [mcu_buttons.Pan, mcu_buttons.Sends, mcu_buttons.Equalizer, mcu_buttons.Stereo, mcu_buttons.Effects, mcu_buttons.Free]:
                if event.data2 > 0:
                    # Because the midi index of the buttons is not in the correct order on the hardware, we need to map the button to the correct mode index
                    modeIndex = mcu_modes.ButtonModeMapping[event.data1]
                    event.handled = True
                    # Propagate the mode change to the extenders FIRST, so they are already in the new mode
                    # when we push them their per-extender track banking offsets.
                    if not self.McuDevice.isExtender:
                        self.McuDevice.SendButtonPressToExtenders(event.data1) # this is how mode changes are communicated to the extenders as well, by sending a "fake" button press for the mode button that was pressed
                    if self.Mode != self.modes[modeIndex]:
                        print('Switching to mode: ' + mcu_constants.ModeShortDescriptions[modeIndex])
                        self.EnableMode(self.modes[modeIndex])
                        self.OnSendMsg(mcu_constants.ModeDescriptions[modeIndex])
                    else:
                        # when pressing the button of the currently active mode while it's already active, we reset the track banking to the first bank
                        print('Resetting track manager')
                        if not self.McuDevice.isExtender:
                            self.mixerTrackManager.SetFirstTrackIndex(0)
                            self.effectsSlotTrackManager.SetFirstTrackIndex(0)
                            self.effectsParamTrackManager.SetFirstTrackIndex(0)
                            self.eqTrackManager.SetFirstTrackIndex(0)
                            self.OnSendMsg('Track banking has been reset.')
                    event.handled = True
                    return event

        # handle MIDI message in behaviors and mode
        for behavior in self.PermanentBehaviors:
            behavior.OnMidiMsg(event)
        if (self.Mode != None):
            self.Mode.OnMidiMsg(event)

    def OnUpdateBeatIndicator(self, Value):
        """ Called when beat indicator has updated value """
        for behavior in self.PermanentBehaviors:
            behavior.OnUpdateBeatIndicator(Value)
        if (self.Mode != None):
            self.Mode.OnUpdateBeatIndicator(Value)

    def OnWaitingForInput(self):
        """ Called when FL studio is in waiting mode """
        for behavior in self.PermanentBehaviors:
            behavior.OnWaitingForInput()
        if (self.Mode != None):
            self.Mode.OnWaitingForInput()
