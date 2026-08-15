import device
import midi
import channels
import plugins

from behaviors.mcu_base_screen_behavior import McuBaseScreenBehavior
from constants.mcu_constants import ScribbleStripWidth
from device_hal.mcu_colors import GetMcuColor, ScreenColorBlack, WhiteColor
from device_hal.mcu_device import McuDevice
from utilities.track_banking_manager import TrackBankingManager
from utilities.transliteration import TransliterateToAscii
from utilities.channel_rack_mode_state import ChannelRackModeState
from utilities.channel_param_mapper import ChannelParamMapper
from utilities.effects_param_format import FormatEffectParameterValue
from utilities.plugin_param_config import PluginParamConfig
from utilities.scribble_strip_text import StripSpacesIfOverWidth, CenterToWidth

class ChannelParamScreenBehavior(McuBaseScreenBehavior):
    """
    Screen behavior for the Channel Rack parameter view.

    Shows the opened generator's parameter names (top row) and values (bottom row) for the parameters
    currently banked onto this unit. The target generator is the channel the view locked onto when it was
    opened (ChannelRackModeState), and only the generator's real, named parameters are shown: a banked
    virtual index is translated to its FL parameter index through ChannelParamMapper.Map.
    """

    def __init__(self, mcuDevice: McuDevice, trackBankingManager: TrackBankingManager, state: ChannelRackModeState):
        super().__init__(mcuDevice, trackBankingManager)
        self.__state = state

    def OnEnable(self):
        super().OnEnable()
        self.RenderScreen()

    # Also re-render the screen when idle, to react to changes done by an automation clip
    # (those don't trigger any refresh flags).
    def OnIdle(self):
        super().OnIdle()
        # Don't repaint over a temporary message; the base restores the screen when it expires.
        if not self._isShowingTempMessage:
            self.RenderScreen()

    def OnRefresh(self, flags):
        super().OnRefresh(flags)

        # Plugin parameter values report changes via HW_Dirty_ControlValues; also refresh on channel events.
        if flags & (midi.HW_Dirty_ControlValues | midi.HW_ChannelEvent): # and not self._isShowingTempMessage:
            self.RenderScreen()

    def RenderScreen(self):
        """Render the parameter names and values for the params banked on this unit."""
        channel = self.__state.channel
        valid = channel >= 0 and channel < channels.channelCount(True)

        topText = ''
        bottomText = ''
        colorArr = []

        try:
            for virtualIndex in self._trackBanking.GetTrackIndexes():
                if valid and self._trackBanking.VirtualTrackExists(virtualIndex):
                    realIndex = ChannelParamMapper.Map[virtualIndex]
                    name = TransliterateToAscii(plugins.getParamName(realIndex, channel, -1, True)).strip()
                    name = StripSpacesIfOverWidth(name, ScribbleStripWidth)
                    topText += CenterToWidth(name, ScribbleStripWidth)

                    paramValue = plugins.getParamValue(realIndex, channel, -1, True)
                    valueStr = TransliterateToAscii(plugins.getParamValueString(realIndex, channel, -1, useGlobalIndex=True))
                    display = FormatEffectParameterValue(valueStr, paramValue, ScribbleStripWidth)
                    bottomText += CenterToWidth(display, ScribbleStripWidth)

                    color = PluginParamConfig.GetColor(self.__state.pluginName, realIndex)
                    colorArr.append(color if color is not None else WhiteColor)
                else:
                    topText += ' ' * ScribbleStripWidth
                    bottomText += ' ' * ScribbleStripWidth
                    colorArr.append(GetMcuColor(ScreenColorBlack))
        except RuntimeError:
            # FL raises "Operation unsafe at current time" when queried while a modal is open (e.g. the
            # F2 rename box). Skip this render; a later refresh/idle repaints once FL is safe again.
            return

        if (device.isAssigned()):
            self.McuDevice.SetTextDisplay(topText, 0, skipIsAssignedCheck=True)
            self.McuDevice.SetTextDisplay(bottomText, 1, skipIsAssignedCheck=True)
            self.McuDevice.SetScreenColors(colorArr, skipIsAssignedCheck=True)
