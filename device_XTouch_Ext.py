# name=FLtouch X-Touch Extender
# url=https://forum.image-line.com/viewtopic.php?f=1994&t=269919
# receiveFrom=FLtouch X-Touch
# supportedDevices=X-Touch-Ext

from device_hal.mcu_device import McuDevice
import mcu_base_class

class TMackieCU_Ext(mcu_base_class.McuBaseClass):
    def __init__(self):
        super().__init__(McuDevice(True))

    def OnInit(self):
        super().OnInit()

    def OnDeInit(self):
        super().OnDeInit()
        print('OnDeInit ready')

    def OnRefresh(self, flags):
        super().OnRefresh(flags)

    def OnMidiMsg(self, event):
        super().OnMidiMsg(event)

    def OnSysEx(self, event):
        super().OnSysEx(event)

    def OnSendMsg(self, Msg: str, duration: int = 2000):
        super().OnSendMsg(Msg, duration)


MackieCU_Ext = TMackieCU_Ext()

def OnInit():
    MackieCU_Ext.OnInit()

def OnDeInit():
    MackieCU_Ext.OnDeInit()

def OnDirtyMixerTrack(SetTrackNum):
    MackieCU_Ext.OnDirtyMixerTrack(SetTrackNum)

def OnDirtyChannel(index, flag=0):
    MackieCU_Ext.OnDirtyChannel(index)

def OnRefresh(Flags):
    MackieCU_Ext.OnRefresh(Flags)

def OnMidiMsg(event):
    MackieCU_Ext.OnMidiMsg(event)

def OnSysEx(event):
    MackieCU_Ext.OnSysEx(event)

def OnSendTempMsg(Msg, Duration = 1000):
    MackieCU_Ext.OnSendMsg(Msg)

def OnUpdateMeters():
    MackieCU_Ext.OnUpdateMeters()

def OnIdle():
    MackieCU_Ext.OnIdle()
