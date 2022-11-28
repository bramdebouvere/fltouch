import device
import midi

import mcu_device_track_meter
import mcu_device_track_fader
import mcu_device_track_buttons

class McuDeviceTrack:
    """ Class for controlling a single track on the Xtouch in MCU mode (Hardware abstraction) """

    def __init__(self, index: int, productId: int, isMain: bool):
        self._index = index
        self._baseMidiValue = 48 + index * 6
        self._productId = productId

        # whether or not the main (master) track
        self._isMain = isMain

        # create track meter instance, the master track does not have a meter
        self._meter = None if self.isMain else mcu_device_track_meter.McuDeviceTrackMeter(productId, index)
        self._fader = mcu_device_track_fader.McuDeviceTrackFader(productId, index, isMain, self._baseMidiValue)
        self._buttons = mcu_device_track_buttons.McuDeviceTrackButtons(productId, index, self.baseMidiValue)

    @property
    def index(self):
        return self._index

    @property
    def baseMidiValue(self):
        """ The base MIDI value of the track, where midi values of the buttons and sliders on that track are based on """
        return self._baseMidiValue

    @property
    def isMain(self):
        """ Whether or not this is the master volume track """
        return self._isMain

    @property
    def meter(self):
        """ Returns an instance of the DB meter for this track (None if Main track) """
        return self._meter

    @property
    def fader(self):
        """ Returns an instance of the automated fader for this track """
        return self._fader

    @property
    def buttons(self):
        """ Returns an instance of the buttons for this track """
        return self._buttons

    @property
    def productId(self):
        """ Returns the productId of the MCU device """
        return self._productId
