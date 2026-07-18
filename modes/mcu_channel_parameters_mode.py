import midi
import channels
import plugins

from behaviors.channel_param_screen_behavior import ChannelParamScreenBehavior
from behaviors.channel_param_encoder_behavior import ChannelParamEncoderBehavior
from behaviors.channel_param_select_button_behavior import ChannelParamSelectButtonBehavior
from behaviors.channel_namevalue_button_behavior import ChannelNameValueButtonBehavior
from behaviors.fader_touch_suppress_behavior import FaderTouchSuppressBehavior
from behaviors.plugin_picker_button_behavior import PluginPickerButtonBehavior
from behaviors.track_banking_behavior import TrackBankingBehavior
from device_hal.mcu_device import McuDevice
from modes.mcu_base_mode import McuBaseMode
from utilities import channel_rack_mode_state
from utilities.channel_rack_mode_state import ChannelRackModeState
from utilities.channel_param_mapper import ChannelParamMapper
from utilities.track_banking_manager import TrackBankingManager

class McuChannelParametersMode(McuBaseMode):
    """
    Channel Rack mode parameter view sub-mode.

    Shows the opened generator's parameters across the strips (banked through the parameter banking
    manager). Encoder = parameter value (press reverts to the value captured on entry), screen =
    parameter name + value. SELECT returns to the channel overview.

    The view is locked to the generator captured in ChannelRackModeState by McuChannelRackMode.OnModeSwitch.
    If the generator is removed or swapped while this sub-mode is active the main unit detects it and
    requests a return to the channel overview (extenders follow via sync).
    """

    def __init__(self, device: McuDevice, paramBankingManager: TrackBankingManager,
                 state: ChannelRackModeState, compositeMode):
        self._state = state
        self._compositeMode = compositeMode
        screenBehavior = ChannelParamScreenBehavior(device, paramBankingManager, state)
        super().__init__(device, [
            screenBehavior,
            ChannelParamEncoderBehavior(device, paramBankingManager, state),
            TrackBankingBehavior(device, paramBankingManager),
            ChannelParamSelectButtonBehavior(device, compositeMode),
            ChannelNameValueButtonBehavior(device, screenBehavior),
            PluginPickerButtonBehavior(device, 0), # category 0 = plugin picker generators
            FaderTouchSuppressBehavior(device),
        ], paramBankingManager)

    def OnEnable(self):
        # Build the [virtual -> real] parameter map and size the banking to it before any behavior activates
        ChannelParamMapper.CreateMapForChannel(self._state.channel)
        assert self._trackBankingManager is not None
        self._trackBankingManager.softwareTrackCount = len(ChannelParamMapper.Map)

        # enable behaviors + banking manager
        super().OnEnable()

        # Reset param banking when entering the parameter view
        if not self.McuDevice.isExtender:
            self._trackBankingManager.SetFirstTrackIndex(0)

    def OnRefresh(self, flags):
        if not self._enabled:
            return

        # Main unit only: detect the locked generator being removed or swapped; exit to overview.
        # Extenders follow via the sub-mode sync message that the main dispatches.
        if not self.McuDevice.isExtender:
            channel = self._state.channel

            if channel < 0 or channel >= channels.channelCount(True):
                self._compositeMode.SwitchTo(channel_rack_mode_state.OVERVIEW)
                return

            # When the generator name changes (plugin gets replaced), exit to overview
            if (flags & (midi.HW_Dirty_Names | midi.HW_ChannelEvent)) and \
                    plugins.getPluginName(channel, -1, False, True) != self._state.pluginName:
                self._compositeMode.SwitchTo(channel_rack_mode_state.OVERVIEW)
                return

        super().OnRefresh(flags)
