import ui
import midi
import channels

from behaviors.channel_screen_behavior import ChannelScreenBehavior
from behaviors.channel_fader_behavior import ChannelFaderBehavior
from behaviors.channel_encoder_pan_behavior import ChannelEncoderPanBehavior
from behaviors.channel_mute_button_behavior import ChannelMuteButtonBehavior
from behaviors.channel_solo_button_behavior import ChannelSoloButtonBehavior
from behaviors.channel_select_button_behavior import ChannelSelectButtonBehavior
from behaviors.channel_namevalue_button_behavior import ChannelNameValueButtonBehavior
from behaviors.plugin_picker_button_behavior import PluginPickerButtonBehavior
from behaviors.track_banking_behavior import TrackBankingBehavior
from behaviors.channel_show_bank_in_fl_behavior import ChannelShowBankInFLBehavior
from behaviors.jogwheel_behavior import JogWheelBehavior
from device_hal.mcu_device import McuDevice
from modes.mcu_base_mode import McuBaseMode
from utilities.track_banking_manager import TrackBankingManager

class McuChannelOverviewMode(McuBaseMode):
    """
    Channel Rack mode overview sub-mode.

    Spreads all of the project's channel-rack channels across the strips (banked through the channel
    banking manager, using the global channel index). Fader = channel volume, encoder = pan, MUTE/SOLO
    buttons = mute/solo, screen = channel number + name in the channel's colour, SELECT = open the
    generator and switch to the parameter sub-mode, Smooth = add a generator (plugin picker).
    """

    def __init__(self, device: McuDevice, channelRackManager: TrackBankingManager, compositeMode):
        screenBehavior = ChannelScreenBehavior(device, channelRackManager)
        super().__init__(device, [
            screenBehavior,
            ChannelFaderBehavior(device, channelRackManager),
            ChannelEncoderPanBehavior(device, channelRackManager),
            ChannelMuteButtonBehavior(device, channelRackManager),
            ChannelSoloButtonBehavior(device, channelRackManager),
            ChannelSelectButtonBehavior(device, channelRackManager, compositeMode),
            ChannelNameValueButtonBehavior(device, screenBehavior),
            TrackBankingBehavior(device, channelRackManager),
            ChannelShowBankInFLBehavior(device, channelRackManager),
            PluginPickerButtonBehavior(device, 0), # category 0 = plugin picker for generators
            JogWheelBehavior(device, screenBehavior),
        ], channelRackManager)

    def OnEnable(self):
        # Make the channel rack visible and focused whenever the overview becomes active (this includes
        # returning from the parameter view). Only the main unit drives FL windows.
        if not self.McuDevice.isExtender:
            ui.showWindow(midi.widChannelRack)
            ui.setFocused(midi.widChannelRack)

        # Size the banking to the current channel count before behaviors paint.
        assert self._trackBankingManager is not None
        self._trackBankingManager.softwareTrackCount = channels.channelCount(True)

        super().OnEnable()

    def OnRefresh(self, flags):
        if not self._enabled:
            return

        # Keep the banking bounds in sync as channels are added/removed (e.g. via the plugin picker).
        if flags & (midi.HW_ChannelEvent | midi.HW_Dirty_ChannelRackGroup):
            assert self._trackBankingManager is not None
            self._trackBankingManager.softwareTrackCount = channels.channelCount(True)

        super().OnRefresh(flags)

    def OnDirtyChannel(self, index):
        if not self._enabled:
            return

        # Update the max banking before behaviors repaint, so an added/removed channel is reflected.
        assert self._trackBankingManager is not None
        self._trackBankingManager.softwareTrackCount = channels.channelCount(True)

        super().OnDirtyChannel(index)
