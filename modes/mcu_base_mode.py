import midi

from behaviors.mcu_base_behavior import McuBaseBehavior
from utilities.fl_class_import import FlMidiMsg

from device_hal.mcu_device import McuDevice
from device_hal import mcu_buttons

class McuBaseMode():
    """
    This is the base class for an Mcu Mode. A mode controls all behaviours of the main mackie unit.
    The hardware can have different functionality depending on the mode.
    
    To use this class, you need to create a class that inherits from this class and override the methods you want to use.
    """

    def __init__(self, device: McuDevice, behaviors: list[McuBaseBehavior], trackBankingManager = None):
        self._mcuDevice = device
        self._behaviors = behaviors
        self._enabled = False
        self._trackBankingManager = trackBankingManager

    @property
    def McuDevice(self) -> McuDevice:
        return self._mcuDevice
    
    @property
    def Enabled(self) -> bool:
        return self._enabled

    def OnEnable(self):
        """ Called when the mode has been enabled """
        self._enabled = True
        for behavior in self._behaviors:
            behavior.OnEnable()
        if self._trackBankingManager is not None:
            self._trackBankingManager.Enable()

    def OnDisable(self):
        """ Called before the mode will be disabled """
        if self._trackBankingManager is not None:
            self._trackBankingManager.Disable()
        for behavior in self._behaviors:
            behavior.OnDisable()
        self._enabled = False

    def OnDirtyMixerTrack(self, SetTrackNum):
        """
        Called on mixer track(s) change, 'SetTrackNum' indicates track index of track that changed or -1 when all tracks changed
        collect info about 'dirty' tracks here but do not handle track(s) refresh, wait for OnRefresh event with HW_Dirty_Mixer_Controls flag
        """
        if (not self._enabled):
            return
        for behavior in self._behaviors:
            behavior.OnDirtyMixerTrack(SetTrackNum)

    def OnDirtyChannel(self, index):
        """ Called on Channel Rack channel change. 'index' indicates channel index of channel that changed or -1 when all channels changed. """
        if (not self._enabled):
            return
        for behavior in self._behaviors:
            behavior.OnDirtyChannel(index)

    def OnUpdateMeters(self):
        """ Called when peak meters have updated values """
        if (not self._enabled):
            return
        for behavior in self._behaviors:
            behavior.OnUpdateMeters()

    def OnIdle(self):
        """ Called from time to time. Can be used to do some small tasks, mostly UI related """
        if (not self._enabled):
            return
        for behavior in self._behaviors:
            behavior.OnIdle()

    def OnSendTempMsg(self, msg: str, duration = 2000):
        """ Called when hint message (to be displayed on controller display) is sent to the controller. The duration of message is in ms. """
        if (not self._enabled):
            return
        for behavior in self._behaviors:
            behavior.OnSendTempMsg(msg, duration)

    def OnRefresh(self, flags):
        """ Called when something changed that the script might want to respond to. 
            - flags:
            HW_Dirty_Mixer_Sel 	        1 	    mixer selection changed
            HW_Dirty_Mixer_Display 	    2 	    mixer display changed
            HW_Dirty_Mixer_Controls     4 	    mixer controls changed
            HW_Dirty_RemoteLinks 	    16 	    remote links (linked controls) has been added/removed
            HW_Dirty_FocusedWindow 	    32 	    channel selection changed
            HW_Dirty_Performance 	    64 	    performance layout changed
            HW_Dirty_LEDs 	            256     various changes in FL which require update of controller leds
                                                update status leds (play/stop/record/active window/.....) on this flag
            HW_Dirty_RemoteLinkValues 	512 	remote link (linked controls) value is changed
            HW_Dirty_Patterns 	        1024 	pattern changes
            HW_Dirty_Tracks 	        2048 	track changes
            HW_Dirty_ControlValues 	    4096 	plugin cotrol value changes
            HW_Dirty_Colors 	        8192 	plugin colors changes
            HW_Dirty_Names 	            16384 	plugin names changes
            HW_Dirty_ChannelRackGroup 	32768 	Channel rack group changes
            HW_ChannelEvent 	        65536 	channel changes
        """
        if (not self._enabled):
            return
        for behavior in self._behaviors:
            behavior.OnRefresh(flags)

    def OnMidiMsg(self, event: FlMidiMsg):
        """ Called for all MIDI messages. """
        if (not self._enabled):
            return
            
        # Pass to behaviors
        for behavior in self._behaviors:
            behavior.OnMidiMsg(event)

    def OnSysEx(self, event: FlMidiMsg):
        """ Called for all SysEx messages. """
        if (not self._enabled):
            return
        for behavior in self._behaviors:
            behavior.OnSysEx(event)

    def OnFirstConnect(self):
        """ Called when device is connected for the first time (ever) """
        if (not self._enabled):
            return
        for behavior in self._behaviors:
            behavior.OnFirstConnect()

    def OnProjectLoad(self, status: int):
        """ Called when project is loaded """
        if (not self._enabled):
            return
        for behavior in self._behaviors:
            behavior.OnProjectLoad(status)

    def OnUpdateBeatIndicator(self, value: int):
        """ Called when the beat indicator has changes - "value" can be off = 0, bar = 1 (on), beat = 2 (on) """
        if (not self._enabled):
            return
        for behavior in self._behaviors:
            behavior.OnUpdateBeatIndicator(value)


    def OnWaitingForInput(self):
        """ Called when FL studio is in waiting mode """
        if (not self._enabled):
            return
        for behavior in self._behaviors:
            behavior.OnWaitingForInput()
