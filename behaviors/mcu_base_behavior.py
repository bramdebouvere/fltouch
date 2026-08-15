from device_hal.mcu_device import McuDevice

from utilities.fl_class_import import FlMidiMsg

class McuBaseBehavior():
    """
    Shared base class for behavior scripts for both the extender and the main mackie unit.
    To use this class, you need to create a class that inherits from this class and override the methods you want to use.
    """

    def __init__(self, device: McuDevice):
        self.McuDevice = device

    def OnEnable(self):
        """ Called when the behavior has been enabled """
        pass

    def OnDisable(self):
        """ Called before the behavior will be disabled """
        pass

    def OnDirtyMixerTrack(self, SetTrackNum):
        """
        Called on mixer track(s) change, 'SetTrackNum' indicates track index of track that changed or -1 when all tracks changed
        collect info about 'dirty' tracks here but do not handle track(s) refresh, wait for OnRefresh event with HW_Dirty_Mixer_Controls flag
        """
        pass

    def OnDirtyChannel(self, index):
        """
        Called when a Channel Rack channel changes ('index' is the changed channel, or -1 for all). This is
        the channel-rack analog of OnDirtyMixerTrack
        """
        pass

    def OnUpdateMeters(self):
        """ Called when peak meters have updated values """
        pass

    def OnIdle(self):
        """ Called from time to time. Can be used to do some small tasks, mostly UI related. For example: update activity meters. """
        pass

    def OnSendTempMsg(self, msg: str, duration = 2000):
        """ Called when hint message (to be displayed on controller display) is sent to the controller. The duration of message is in ms. """
        pass

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
            HW_Dirty_ControlValues 	    4096 	plugin control value changes
            HW_Dirty_Colors 	        8192 	plugin colors changes
            HW_Dirty_Names 	            16384 	plugin names changes
            HW_Dirty_ChannelRackGroup 	32768 	Channel rack group changes
            HW_ChannelEvent 	        65536 	channel changes
            HW_Dirty_Undo 	            131072 	Undo history changes (version 42)
            HW_Dirty_ChannelRackGroup 	262144 	Undo history changes (version 42)
        """
        pass

    def OnMidiMsg(self, event: FlMidiMsg):
        """ Called for all MIDI messages. """
        return event

    def OnSysEx(self, event: FlMidiMsg):
        """ Called for all SysEx messages. """
        pass

    def OnFirstConnect(self):
        """ Called when device is connected for the first time (ever) """
        pass

    def OnProjectLoad(self, status: int):
        """ Called when project is loaded """
        pass

    def OnUpdateBeatIndicator(self, value: int):
        """ Called when the beat indicator has changes - "value" can be off = 0, bar = 1 (on), beat = 2 (on) """
        pass

    def OnWaitingForInput(self):
        """ Called when FL studio is in waiting mode """
        pass

