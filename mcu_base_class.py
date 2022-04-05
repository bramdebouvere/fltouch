import device
import ui
import time
import utils
import mixer
import midi

import mcu_constants
import mcu_device
import mcu_track
import mcu_pages


class McuBaseClass():
    """ Shared base class for both the extender and the main mackie unit """

    def __init__(self, device: mcu_device.McuDevice):
        self.MsgT = ["", ""]
        self.Tracks = [mcu_track.McuTrack() for i in range(0)] # empty array, since "import typing" is not supported

        self.Shift = False #indicates that the shift button is pressed
        self.MsgDirty = False

        self.FirstTrack = 0
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
