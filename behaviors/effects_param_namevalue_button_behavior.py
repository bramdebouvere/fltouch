import midi
import mixer
import transport
import general
import device

from behaviors.mcu_base_behavior import McuBaseBehavior
from behaviors.mcu_base_screen_behavior import McuBaseScreenBehavior
from device_hal import mcu_buttons
from device_hal.mcu_colors import GetMcuColor, TrackColorCycle, DefaultTrackColor
from device_hal.mcu_device import McuDevice
from utilities.button_manager import ButtonManager
from utilities.effects_mode_state import EffectsModeState

class EffectsParamNameValueButtonBehavior(McuBaseBehavior):
    """
    Handles the Name/Value button while the Effects parameter view is active.

    - Name/Value: trigger rename (F2). The opened plugin is already the focused window, so F2 targets it.
    - Shift+Name/Value: cycle the opened effect slot's colour (mirrors the mixer-track and channel colour
      cycles, but recolours the individual FX slot via mixer.setSlotColor).

    Targets the plugin locked into EffectsModeState on entry (its track + slot), not the live mixer
    selection.

    NOTE: mixer.setSlotColor only works from scripting FL Studio 2026 (scripting v41); earlier versions
    have a bug where the color is never applied or read back (tested broken on 25.5.2 - see
    https://forum.image-line.com/viewtopic.php?t=340671). On older versions the color cycle is disabled
    and a message asks the user to update FL Studio.
    """

    def __init__(self, mcuDevice: McuDevice, state: EffectsModeState, screenBehavior: McuBaseScreenBehavior):
        super().__init__(mcuDevice)
        self._state = state
        self._screenBehavior = screenBehavior

    def OnMidiMsg(self, event):
        if event.midiId != midi.MIDI_NOTEON:
            return super().OnMidiMsg(event)
        if event.data1 != mcu_buttons.NameValue:
            return super().OnMidiMsg(event)

        if event.data2 > 0:
            if ButtonManager.ShiftPressed:
                if general.getVersion() >= 41:
                    self._CycleSlotColor()
                else:
                    self._screenBehavior.OnSendTempMsg('Update FL Studio to recolor FX slots', 3000)
            else:
                transport.globalTransport(midi.FPT_F2, 2, event.pmeFlags, 8)

        event.handled = True
        return event

    def _CycleSlotColor(self):
        """Cycles the opened effect slot's colour through the MCU's available colors, then back to the default."""
        track = self._state.track
        slot = self._state.slot
        if track < 0 or slot < 0:
            return

        currentBucket = GetMcuColor(mixer.getSlotColor(track, slot))

        buckets = [bucket for bucket, _ in TrackColorCycle]
        if currentBucket in buckets:
            nextIndex = buckets.index(currentBucket) + 1
            if nextIndex < len(TrackColorCycle):
                mixer.setSlotColor(track, slot, TrackColorCycle[nextIndex][1])
            else:
                mixer.setSlotColor(track, slot, DefaultTrackColor)
        else:
            mixer.setSlotColor(track, slot, TrackColorCycle[0][1])
