import midi
import channels
import transport

from behaviors.mcu_base_behavior import McuBaseBehavior
from behaviors.mcu_base_screen_behavior import McuBaseScreenBehavior
from device_hal import mcu_buttons
from device_hal.mcu_colors import GetMcuColor, TrackColorCycle, DefaultTrackColor
from device_hal.mcu_device import McuDevice
from utilities.button_manager import ButtonManager

class ChannelNameValueButtonBehavior(McuBaseBehavior):
    """
    Handles the Name/Value button in Channel Rack mode.

    - Name/Value: focus the selected channel's plugin, then trigger rename (F2). In the channel rack, F2
      renames the active pattern, so the plugin has to be focused first for the rename to target the
      generator instead.
    - Shift+Name/Value: cycle the selected channel's colour (same as for mixer tracks).
    """

    def __init__(self, mcuDevice: McuDevice, screenBehavior: McuBaseScreenBehavior):
        super().__init__(mcuDevice)
        self._screenBehavior = screenBehavior

    def OnMidiMsg(self, event):
        if event.midiId != midi.MIDI_NOTEON:
            return super().OnMidiMsg(event)
        if event.data1 != mcu_buttons.NameValue:
            return super().OnMidiMsg(event)

        if event.data2 > 0:
            if ButtonManager.ShiftPressed:
                self._CycleChannelColor()
            else:
                if event.pmeFlags & midi.PME_System_Safe:
                    # Focus the selected channel's plugin so the following F2 renames the generator
                    # rather than the active pattern.
                    channel = channels.selectedChannel(indexGlobal=True)
                    channels.focusEditor(channel, True)
                transport.globalTransport(midi.FPT_F2, 2, event.pmeFlags, 8)

        event.handled = True
        return event

    def _CycleChannelColor(self):
        """Cycles the currently selected channel's colour through the MCU's available colors, then back to the default."""
        channel = channels.selectedChannel(indexGlobal=True)
        currentBucket = GetMcuColor(channels.getChannelColor(channel, True))

        buckets = [bucket for bucket, _ in TrackColorCycle]
        if currentBucket in buckets:
            nextIndex = buckets.index(currentBucket) + 1
            if nextIndex < len(TrackColorCycle):
                channels.setChannelColor(channel, TrackColorCycle[nextIndex][1], True)
            else:
                channels.setChannelColor(channel, DefaultTrackColor, True)
        else:
            channels.setChannelColor(channel, TrackColorCycle[0][1], True)

        # FL fires no channel refresh for a colour change, so drive the repaint
        # ourselves: repaint this unit, and broadcast to the extenders (the recoloured channel may be
        # displayed on an extender rather than on the unit whose Name button was pressed).
        self._screenBehavior.RenderScreen()
        self.McuDevice.SendChannelDirtyToExtenders()
