import midi
import channels
import plugins

from utilities.fl_class_import import FlMidiMsg
from behaviors.mode_buttons_behavior import ModeButtonsBehavior
from constants import plugin_menu_items
from device_hal.mcu_device import McuDevice
from device_hal import mcu_buttons
from modes.mcu_composite_mode import McuCompositeMode
from modes.mcu_channel_overview_mode import McuChannelOverviewMode
from modes.mcu_channel_parameters_mode import McuChannelParametersMode
from modes.mcu_menu_mode import McuMenuMode
from utilities import channel_rack_mode_state
from utilities.channel_rack_mode_state import ChannelRackModeState
from utilities.track_banking_manager import TrackBankingManager

class McuChannelRackMode(McuCompositeMode):
    """
    Channel Rack mode: control FL Studio's channel rack generators.

    Composed of three sub-modes:
    - McuChannelOverviewMode (OVERVIEW):    all channels with volume/pan/mute/solo, add generator with global
                                            view (smooth) button, select to open generator
    - McuChannelParametersMode (PARAMS):    edit the opened generator's plugin parameters.
    - McuMenuMode (MENU):                   Flip preset menu overlaid on the parameter view (next/previous preset).
    """

    def __init__(self, device: McuDevice, channelRackManager: TrackBankingManager, channelParamManager: TrackBankingManager):
        self._state = ChannelRackModeState()
        super().__init__(device, [ModeButtonsBehavior(device, mcu_buttons.Free)])

        # sub-modes
        overviewMode = McuChannelOverviewMode(device, channelRackManager, self)
        paramMode = McuChannelParametersMode(device, channelParamManager, self._state, self)
        menuItems = plugin_menu_items.BuildGeneratorMenuItems(self._state)
        menuBankingManager = TrackBankingManager(device, len(menuItems))
        presetMenuMode = McuMenuMode(device, menuBankingManager, self, menuItems,
                                     channel_rack_mode_state.PARAMS, 0) # picker category 0 = generators

        self._addSubMode(channel_rack_mode_state.OVERVIEW, overviewMode)
        self._addSubMode(channel_rack_mode_state.PARAMS, paramMode)
        self._addSubMode(channel_rack_mode_state.MENU, presetMenuMode)

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
            # Only capture the generator when opening from the channel overview. Returning from the
            # preset menu keeps the already-locked generator.
            if self._activeSubModeKey == channel_rack_mode_state.OVERVIEW:
                # The SELECT behavior selects the generator's channel first, and we read the selection back
                # here (global index), so any channel index is handled.
                channel = channels.selectedChannel(indexGlobal=True)
                self._state.channel = channel
                self._state.pluginName = plugins.getPluginName(channel, -1, False, True)
        elif key == channel_rack_mode_state.OVERVIEW:
            # Close the generator window the parameter view opened, if that channel still exists.
            # Main unit drives FL windows.
            if not self.McuDevice.isExtender and 0 <= self._state.channel < channels.channelCount(True):
                channels.showCSForm(self._state.channel, 0, True)  # 0 = hide
            self._state.channel = -1
            self._state.pluginName = ''
