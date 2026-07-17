import midi
import channels
import plugins

from utilities.fl_class_import import FlMidiMsg
from behaviors.mode_buttons_behavior import ModeButtonsBehavior
from device_hal.mcu_device import McuDevice
from device_hal import mcu_buttons
from modes.mcu_composite_mode import McuCompositeMode
from modes.mcu_channel_overview_mode import McuChannelOverviewMode
from modes.mcu_channel_parameters_mode import McuChannelParametersMode
from utilities import channel_rack_mode_state
from utilities.channel_rack_mode_state import ChannelRackModeState
from utilities.track_banking_manager import TrackBankingManager

class McuChannelRackMode(McuCompositeMode):
    """
    Channel Rack mode: control FL Studio's channel rack generators.

    Composed of two sub-modes:
    - McuChannelOverviewMode (OVERVIEW):    all channels with volume/pan/mute/solo, add generator with global 
                                            view (smooth) button, select to open generator
    - McuChannelParametersMode (PARAMS):    edit the opened generator's plugin parameters.
    """

    def __init__(self, device: McuDevice, channelRackManager: TrackBankingManager, channelParamManager: TrackBankingManager):
        self._state = ChannelRackModeState()
        super().__init__(device, [ModeButtonsBehavior(device, mcu_buttons.Free)])

        # sub-modes
        overviewMode = McuChannelOverviewMode(device, channelRackManager, self)
        paramMode = McuChannelParametersMode(device, channelParamManager, self._state, self)

        self._addSubMode(channel_rack_mode_state.OVERVIEW, overviewMode)
        self._addSubMode(channel_rack_mode_state.PARAMS, paramMode)

    def OnMidiMsg(self, event: FlMidiMsg):
        # A channel-dirty broadcast from the main unit (see McuDevice.SendChannelDirtyToExtenders): FL does
        # not report a channel colour change to every unit, so the main unit tells the extenders to repaint.
        # Run the normal dirty-channel path on this unit, which repaints the strips and faders.
        if event.midiId == midi.MIDI_NOTEON and event.data1 == mcu_buttons.ChannelDirtyBroadcast:
            self.OnDirtyChannel(-1) # -1 = all channels dirty
            event.handled = True
            return event
        return super().OnMidiMsg(event)

    def OnModeSwitch(self, key, _data):
        """
        Capture the target generator's channel before the parameter sub-mode enables, or clear the state
        when returning to the channel overview. Implements base class.
        """
        if key == channel_rack_mode_state.PARAMS:
            # The SELECT behavior selects the generator's channel first, and we read the selection back here
            # (global index), so any channel index is handled.
            channel = channels.selectedChannel(indexGlobal=True)
            self._state.channel = channel
            self._state.pluginName = plugins.getPluginName(channel, -1, False, True)
        else: # OVERVIEW
            # Close the generator window the parameter view opened, if that channel still exists.
            # Main unit drives FL windows.
            if not self.McuDevice.isExtender and 0 <= self._state.channel < channels.channelCount(True):
                channels.showCSForm(self._state.channel, 0, True)  # 0 = hide
            self._state.channel = -1
            self._state.pluginName = ''
