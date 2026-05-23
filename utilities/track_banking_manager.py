import device
import midi
import mixer

from constants import mcu_extender_location
from device_hal import mcu_buttons
from device_hal.mcu_device import McuDevice

class TrackBankingManager:
    """
    Manages track banking for the X-Touch, handling both real mixer tracks and virtual tracks (e.g., for FREE mode).
    This is a utility class, not a behavior. Behaviors can subscribe to changes via callbacks.
    """

    def __init__(self, mcuDevice: McuDevice, softwareTrackCount: int | None = None):
        self.McuDevice = mcuDevice
        self.FirstTrack = 0
        self.ExtenderPos = mcu_extender_location.Left # TODO: allow changing this
        self.TrackCount = 8  # Tracks per hardware unit
        self.Enabled = False
        self.softwareTrackCount = softwareTrackCount
        self.initialized = False

        # Subscribers for when first track changes
        self._TrackChangeSubscribers = []


    def Enable(self):
        """ Enable track banking """
        if self.Enabled:
            return
        self.Enabled = True

        # INIT: if this is the main unit, set the first track
        # if this is not the main unit, the track will be set by the main unit by sending a MIDI message to the extender units
        if not self.initialized:
            if not self.McuDevice.isExtender:
                self.SetFirstTrackIndex(0)
            self.initialized = True

    def Disable(self):
        """ Disable track banking """
        if not self.Enabled:
            return
        self.Enabled = False

    def AddTrackChangeSubscriber(self, callback):
        """ Add a callback function to be called when the first track changes. Callback signature: callback(new_first_track) """
        self._TrackChangeSubscribers.append(callback)

    def RemoveTrackChangeSubscriber(self, callback):
        """ Remove a callback function """
        if callback in self._TrackChangeSubscribers:
            self._TrackChangeSubscribers.remove(callback)

    def _NotifyTrackChangeSubscribers(self, newFirstTrackIndex: int):
        """ Notify all subscribers of first track change """
        for callback in self._TrackChangeSubscribers:
            callback(newFirstTrackIndex)

    def SetFirstTrackIndex(self, value: int):
        """
        Set the index of the virtual track number that will appear as first track on the first hardware unit.

        :param value: Track Index
        """
        old_first_track = self.FirstTrack
        if self.McuDevice.isExtender:
            self.FirstTrack = value
        else:
            extenderCount = device.dispatchReceiverCount()
            print('Setting first track to ' + str(value) + '; Extender count: ' + str(extenderCount))
            if (extenderCount == 0):
                self.FirstTrack = 0
            else:
                if self.ExtenderPos == mcu_extender_location.Left:
                    for n in range(0, extenderCount):
                        self.McuDevice.SetFirstTrackOnExtender(n, value + (n * self.TrackCount))
                    self.FirstTrack = value + extenderCount * self.TrackCount
                elif self.ExtenderPos == mcu_extender_location.Right:
                    self.FirstTrack = value
                    for n in range(0, extenderCount):
                        self.McuDevice.SetFirstTrackOnExtender(n, value + ((n + 1) * self.TrackCount))

        # Notify subscribers if changed
        if old_first_track != self.FirstTrack:
            self._NotifyTrackChangeSubscribers(self.FirstTrack)

        # Refresh hardware
        # TODO: decide what to do with this later 
        print('Showing tracks ' + str(self.GetTrackIndexes()) + ' on this device')
        device.hardwareRefreshMixerTrack(-1)

    def NotifyModeChange(self, mode):
        """ Notify extenders of mode change """
        if self.McuDevice.isExtender:
            return
        receiverCount = device.dispatchReceiverCount()
        for n in range(0, receiverCount):
            self.McuDevice.SendMidiToExtender(n, midi.MIDI_NOTEON + (0x7E << 8) + (mode << 16))

    def GetFirstTrackIndex(self):
        """
        Returns the index of the first virtual track that will be displayed on the Xtouch. Note that it's not because an index is returned, that it will also exist in the software.
        For example, if there are only 7 mixer tracks but the first track index is 5, the Xtouch will show tracks 5-12 but only tracks 5-7 will exist in the software.
        """
        return self.FirstTrack

    def GetTrackIndexes(self):
        """
        Returns the indexes of the virtual tracks that will be displayed on the Xtouch. Note that it's not because an index is returned, that it will also exist in the software.
        For example, if there are only 7 mixer tracks but the first track index is 5, the Xtouch will show tracks 5-12 but only tracks 5-7 will exist in the software.
        """
        return [i for i in range(self.FirstTrack, self.FirstTrack + self.TrackCount)]

    def GetTrackIndex(self, hardwareTrackIndex: int):
        """
        Returns the virtual track index for a given hardware track index. For example, if the first track index is 5 and you ask for hardware track index 2, this will return 7.
        Note that it's not because an index is returned, that it will also exist in the software.

        :param hardwareTrackIndex: The index of the track on the hardware (0-7)
        :return: The corresponding virtual track index, or -1 if the hardware track index is out of range
        """
        if (hardwareTrackIndex >= 8):
            return -1
        return self.FirstTrack + hardwareTrackIndex

    def GetHardwareTrackCount(self):
        """ The amount of tracks on the hardware unit """
        return self.TrackCount

    def GetHardwareTrack(self, index: int):
        """
        Returns the hardware track instance for the given virtual track index

        :param index: Track Index
        :return: McuDeviceTrack or None
        """
        if index < self.FirstTrack or index >= self.FirstTrack + self.TrackCount:
            return None
        return self.McuDevice.GetTrack(index - self.FirstTrack)

    def HandleBankButton(self, button: int):
        """
        Handle fader bank buttons: FaderBankLeft (-8), FaderBankRight (+8), FaderChannelLeft (-1), FaderChannelRight (+1)
        """
        index: int

        if button == mcu_buttons.FaderBankLeft:
            index = self.GetFirstTrack() - self.TrackCount
        elif button == mcu_buttons.FaderBankRight:
            index = self.GetFirstTrack() + self.TrackCount
        elif button == mcu_buttons.FaderChannelLeft:
            index = self.GetFirstTrack() - 1
        elif button == mcu_buttons.FaderChannelRight:
            index = self.GetFirstTrack() + 1

        maxTrackCount = self.GetVirtualTrackCount()
        if index < 0:
            index = 0
        elif index > maxTrackCount - 1:
            index = maxTrackCount - 1

        self.SetFirstTrackIndex(index)

    def GetFirstTrack(self):
        """ Returns the index of the first virtual track that is currently set to be displayed on any hardware unit including extenders. """
        trackOffset = (device.dispatchReceiverCount() * self.TrackCount) if self.ExtenderPos == mcu_extender_location.Left else 0
        return self.FirstTrack - trackOffset

    def GetVirtualTrackCount(self):
        """ Returns the amount of virtual tracks that exist in the software. For example, if there are 9 mixer tracks in your FL Studio project, this will be 9. """
        return self.softwareTrackCount if self.softwareTrackCount is not None else mixer.trackCount() -1  # Subtract 1 to exclude selecteed track

    def VirtualTrackExists(self, index: int):
        """ Returns whether a virtual track with the given index exists in the software. For example, if there are 9 mixer tracks in your FL Studio project, VirtualTrackExists(8) will return true but VirtualTrackExists(9) will return false. """
        return index < self.GetVirtualTrackCount()
