# name=FLtouch X-Touch
# url=https://forum.image-line.com/viewtopic.php?f=1994&t=269919
# supportedDevices=X-Touch
# receiveFrom=FLtouch X-Touch Extender

import device
import mcu_base_class

from behaviors.arrow_zoom_buttons_behavior import ArrowZoomButtonsBehavior
from behaviors.function_buttons_behavior import FunctionButtonsBehavior
from behaviors.jog_sources_buttons_behavior import JogSourcesButtonsBehavior
from behaviors.mixer_main_fader_behavior import MixerMainFaderBehavior
from behaviors.system_buttons_behavior import SystemButtonsBehavior
from behaviors.track_marker_buttons_behavior import TrackMarkerBehavior
from behaviors.window_time_buttons_behavior import WindowTimeButtonsBehavior
import constants.mcu_modes as mcu_modes
import device_hal.mcu_buttons as mcu_buttons
from device_hal.mcu_device import McuDevice

from behaviors.time_display_behavior import TimeDisplayBehavior
from behaviors.transport_buttons_behavior import TransportButtonsBehavior
from behaviors.master_transport_section_buttons_behavior import MasterTransportSectionButtonsBehavior
from behaviors.footswitch_buttons_behavior import FootswitchButtonsBehavior

class TMackieCU(mcu_base_class.McuBaseClass):
    def __init__(self):
        super().__init__(McuDevice(False))

        self.PermanentBehaviors.append(TimeDisplayBehavior(self.McuDevice))
        self.PermanentBehaviors.append(MixerMainFaderBehavior(self.McuDevice))
        self.PermanentBehaviors.append(MasterTransportSectionButtonsBehavior(self.McuDevice))
        self.PermanentBehaviors.append(TransportButtonsBehavior(self.McuDevice))
        self.PermanentBehaviors.append(FootswitchButtonsBehavior(self.McuDevice))
        self.PermanentBehaviors.append(WindowTimeButtonsBehavior(self.McuDevice))
        self.PermanentBehaviors.append(SystemButtonsBehavior(self.McuDevice))
        self.PermanentBehaviors.append(TrackMarkerBehavior(self.McuDevice))
        self.PermanentBehaviors.append(JogSourcesButtonsBehavior(self.McuDevice))
        self.PermanentBehaviors.append(FunctionButtonsBehavior(self.McuDevice))
        self.PermanentBehaviors.append(ArrowZoomButtonsBehavior(self.McuDevice))

    def OnInit(self):

        self.hasBeenIdle = False
        super().OnInit()

    def OnFirstIdle(self):
        self.hasBeenIdle = True
        print('OnFirstIdle')

        # SET INITIAL MODE TO PAN
        # Note: XTouch units are running OnInit in on the Main/Extender units in the order that they were physically turned on.
        #       If someone turns on an extender after the main unit, the main unit will run its OnInit before the extender can,
        #       in which case it cannot send the correct first track index to the extender, because the extender is not yet
        #       initialized and cannot receive it.
        #       We need to make sure that all units are initialized before we run the code below. We do that by waiting for
        #       the first Idle to initialize instead of OnInit. This fixes https://github.com/bramdebouvere/fltouch/issues/8
        #
        # - First send the button press to the extenders so they switch to Pan mode and enable it
        #   This enables the track manager on the extenders, so they are ready to receive track banking messages
        self.McuDevice.SendButtonPressToExtenders(mcu_buttons.Pan)
        # - Then enable the Pan mode on the main unit, which will also send the first track index to the extenders
        self.EnableMode(self.modes[mcu_modes.Pan])


    def OnDeInit(self):
        super().OnDeInit()

        if device.isAssigned():
            # clear assignment message
            self.McuDevice.SetAssignmentText(skipIsAssignedCheck = True)

        print('OnDeInit ready')

    def OnRefresh(self, flags):
        super().OnRefresh(flags)

    def OnMidiMsg(self, event):
        super().OnMidiMsg(event)

    def OnSysEx(self, event):
        super().OnSysEx(event)

    def OnSendMsg(self, Msg: str, duration: int = 2000):
        super().OnSendMsg(Msg, duration)

    def OnIdle(self):
        if (not self.hasBeenIdle):
            self.OnFirstIdle()
        super().OnIdle()

    def OnWaitingForInput(self):
        """ Called when FL studio is in waiting mode """
        super().OnWaitingForInput()

MackieCU = TMackieCU()

def OnInit():
    MackieCU.OnInit()

def OnDeInit():
    MackieCU.OnDeInit()

def OnDirtyMixerTrack(SetTrackNum):
    MackieCU.OnDirtyMixerTrack(SetTrackNum)

def OnDirtyChannel(index, flag=0):
    MackieCU.OnDirtyChannel(index)

def OnRefresh(Flags):
    MackieCU.OnRefresh(Flags)

def OnMidiMsg(event):
    MackieCU.OnMidiMsg(event)

def OnSysEx(event):
    MackieCU.OnSysEx(event)

def OnSendTempMsg(Msg, Duration = 1000):
    """ Called when a hint message should be displayed on the controller. The duration of message is in ms. """
    MackieCU.OnSendMsg(Msg)

def OnUpdateBeatIndicator(Value):
    MackieCU.OnUpdateBeatIndicator(Value)

def OnUpdateMeters():
    MackieCU.OnUpdateMeters()

def OnIdle():
    MackieCU.OnIdle()

def OnWaitingForInput():
    MackieCU.OnWaitingForInput()
