import device
import ui
import time
import midi

from behaviors.mcu_base_behavior import McuBaseBehavior
from behaviors.track_banking_behavior import TrackBankingBehavior
from device_hal import mcu_buttons
from utilities.track_banking_manager import TrackBankingManager
import constants.mcu_constants as mcu_constants
from constants import eq_controls
from device_hal.mcu_device import McuDevice
import constants.mcu_modes as mcu_modes
from modes.mcu_base_mode import McuBaseMode
from modes.mcu_effects_mode import McuEffectsMode
from modes.mcu_eq_mode import McuEQMode
from modes.mcu_pan_composite_mode import McuPanCompositeMode
from modes.mcu_sends_composite_mode import McuSendsCompositeMode
from modes.mcu_stereo_composite_mode import McuStereoCompositeMode
from modes.mcu_channel_rack_mode import McuChannelRackMode

class McuBaseClass():
    """ Shared base class for both the extender and the main mackie unit """

    def __init__(self, device: McuDevice):
        self.McuDevice = device

        # create track banking managers
        self.mixerTrackManager = TrackBankingManager(self.McuDevice)
        self.effectsSlotTrackManager = TrackBankingManager(self.McuDevice, mcu_constants.EffectsSlotCount) # banks the 10 effect slots of the selected track (Effects mode, slot overview)
        self.effectsParamTrackManager = TrackBankingManager(self.McuDevice, 0) # banks the focused plugin's parameters (Effects mode, parameter view); count is set at runtime
        self.eqTrackManager = TrackBankingManager(self.McuDevice, eq_controls.EqControlCount) # banks the 9 EQ controls of the selected track
        self.channelRackManager = TrackBankingManager(self.McuDevice, 0) # banks all channel-rack channels (Channel Rack mode, overview); count is set at runtime
        self.channelParamManager = TrackBankingManager(self.McuDevice, 0) # banks the opened generator's parameters (Channel Rack mode, parameter view); count is set at runtime

        # create modes
        self.modes: dict[int, McuBaseMode] = {
            mcu_modes.Pan: McuPanCompositeMode(self.McuDevice, self.mixerTrackManager),
            mcu_modes.Sends: McuSendsCompositeMode(self.McuDevice, self.mixerTrackManager),
            mcu_modes.Equalizer: McuEQMode(self.McuDevice, self.eqTrackManager),
            mcu_modes.Stereo: McuStereoCompositeMode(self.McuDevice, self.mixerTrackManager),
            mcu_modes.Effects: McuEffectsMode(self.McuDevice, self.effectsSlotTrackManager, self.effectsParamTrackManager),
            mcu_modes.Free: McuChannelRackMode(self.McuDevice, self.channelRackManager, self.channelParamManager)
        }

        self.Mode: McuBaseMode | None = None # the current mode

        self.PermanentBehaviors: list[McuBaseBehavior] = []

        self.MsgDirty = False

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

        if device.isAssigned():
            if ui.isClosing():
                if (self.Mode != None):
                    self.Mode.OnDisable()
                    self.Mode = None
                self.McuDevice.SetTextDisplay('FLTouch session closed at ' + time.ctime(time.time()), 0)
                self.McuDevice.SetTextDisplay('Please consider donating if this script is useful to you', 1)
                self.McuDevice.SetScreenColors()

    def OnDirtyMixerTrack(self, SetTrackNum):
        """
        Called on mixer track(s) change, 'SetTrackNum' indicates track index of track that changed or -1 when all tracks changed
        collect info about 'dirty' tracks here but do not handle track(s) refresh, wait for OnRefresh event with HW_Dirty_Mixer_Controls flag
        """
        for behavior in self.PermanentBehaviors:
            behavior.OnDirtyMixerTrack(SetTrackNum)
        if (self.Mode != None):
            self.Mode.OnDirtyMixerTrack(SetTrackNum)

    def OnDirtyChannel(self, index):
        """ Called on Channel Rack channel change (channel-rack analog of OnDirtyMixerTrack). """
        for behavior in self.PermanentBehaviors:
            behavior.OnDirtyChannel(index)
        if (self.Mode != None):
            self.Mode.OnDirtyChannel(index)

    def OnUpdateMeters(self):
        """ Called when peak meters have updated values """
        for behavior in self.PermanentBehaviors:
            behavior.OnUpdateMeters()
        if (self.Mode != None):
            self.Mode.OnUpdateMeters()

    def OnIdle(self):
        """ Called from time to time. Can be used to do some small tasks, mostly UI related """
        for behavior in self.PermanentBehaviors:
            behavior.OnIdle()
        if (self.Mode != None):
            self.Mode.OnIdle()

    def OnSendMsg(self, Msg: str, duration: int = 2000):
        for behavior in self.PermanentBehaviors:
            behavior.OnSendTempMsg(Msg, duration)
        if (self.Mode != None):
            self.Mode.OnSendTempMsg(Msg, duration)

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
                            self.channelRackManager.SetFirstTrackIndex(0)
                            self.channelParamManager.SetFirstTrackIndex(0)
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
