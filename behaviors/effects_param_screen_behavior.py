import device
import midi
import mixer
import plugins

from behaviors.mcu_base_screen_behavior import McuBaseScreenBehavior
from constants.mcu_constants import ScribbleStripWidth
from device_hal.mcu_colors import GetMcuColor, ScreenColorBlack, WhiteColor
from device_hal.mcu_device import McuDevice
from utilities.track_banking_manager import TrackBankingManager
from utilities.transliteration import TransliterateToAscii
from utilities.effects_mode_state import EffectsModeState
from utilities.effects_param_mapper import EffectsParamMapper
from utilities.effects_param_format import FormatEffectParameterValue
from utilities.plugin_param_config import PluginParamConfig
from utilities.scribble_strip_text import StripSpacesIfOverWidth, CenterToWidth

class EffectsParamScreenBehavior(McuBaseScreenBehavior):
    """
    Screen behavior for the Effects parameter view.

    Shows the opened plugin's parameter names (top row) and values (bottom row) for the parameters
    currently banked onto this unit. The target plugin is the track + slot the view locked onto when it
    was opened (EffectsModeState), and only the plugin's real, named parameters are shown: a banked
    virtual index is translated to its FL parameter index through EffectsParamMapper.Map.
    """

    def __init__(self, mcuDevice: McuDevice, trackBankingManager: TrackBankingManager, state: EffectsModeState):
        super().__init__(mcuDevice, trackBankingManager)
        self.__state = state

    def OnEnable(self):
        super().OnEnable()
        self.RenderScreen()

    # We also need to re-render the screen when idle, to react to changes done by an automation clip
    # Those don't trigger any refresh flags.
    def OnIdle(self):
        super().OnIdle()
        # Don't repaint over a temporary message (e.g. the "update FL Studio" notice); the base restores
        # the screen when the message expires.
        if not self._isShowingTempMessage:
            self.RenderScreen()

    def OnRefresh(self, flags):
        super().OnRefresh(flags)

        # Plugin parameter values report changes via HW_Dirty_ControlValues (and HW_Dirty_Mixer_Controls);
        # the view is locked to its plugin, so a mixer selection change is not a render trigger.
        if flags & (midi.HW_Dirty_Mixer_Controls | midi.HW_Dirty_ControlValues) and not self._isShowingTempMessage:
            self.RenderScreen()

    def RenderScreen(self):
        """Render the parameter names, values and the plugin colour for the params banked on this unit."""
        track = self.__state.track
        slot = self.__state.slot
        valid = track >= 0 and slot >= 0 and mixer.isTrackPluginValid(track, slot)

        topText = ''
        bottomText = ''
        colorArr = []

        try:
            for virtualIndex in self._trackBanking.GetTrackIndexes():
                if valid and self._trackBanking.VirtualTrackExists(virtualIndex):
                    realIndex = EffectsParamMapper.Map[virtualIndex]
                    name = TransliterateToAscii(plugins.getParamName(realIndex, track, slot)).strip()
                    name = StripSpacesIfOverWidth(name, ScribbleStripWidth)
                    topText += CenterToWidth(name, ScribbleStripWidth)

                    paramValue = plugins.getParamValue(realIndex, track, slot)
                    valueStr = TransliterateToAscii(plugins.getParamValueString(realIndex, track, slot))
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
