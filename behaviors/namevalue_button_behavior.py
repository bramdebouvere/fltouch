import midi
import mixer
import transport
from behaviors.mcu_base_behavior import McuBaseBehavior
from behaviors.mcu_base_screen_behavior import McuBaseScreenBehavior
from device_hal import mcu_buttons
from device_hal.mcu_colors import GetMcuColor, TrackColorCycle, DefaultTrackColor
from device_hal.mcu_device import McuDevice
from utilities.button_manager import ButtonManager
from utilities.track_banking_manager import TrackBankingManager

class NameValueButtonBehavior(McuBaseBehavior):
    """Handles the Name/Value button: triggers rename (F2), or Shift+Name/Value to cycle the selected track's color"""

    def __init__(self, mcuDevice, trackBankingManager, screenBehavior):
        super().__init__(mcuDevice)
        self._trackBankingManager = trackBankingManager
        self._screenBehavior = screenBehavior

    def OnMidiMsg(self, event):
        if event.midiId != midi.MIDI_NOTEON:
            return super().OnMidiMsg(event)
        if event.data1 != mcu_buttons.NameValue:
            return super().OnMidiMsg(event)

        if event.data2 > 0:
            if ButtonManager.ShiftPressed:
                self._CycleTrackColor()
            else:
                transport.globalTransport(midi.FPT_F2, 2, event.pmeFlags, 8)

        event.handled = True
        return event

    def _CycleTrackColor(self):
        """Cycles the currently selected mixer track's color through the MCU's available colors, then back to the default."""
        trackNum = mixer.trackNumber()
        currentBucket = GetMcuColor(mixer.getTrackColor(trackNum))

        buckets = [bucket for bucket, _ in TrackColorCycle]
        if currentBucket in buckets:
            nextIndex = buckets.index(currentBucket) + 1
            if nextIndex < len(TrackColorCycle):
                mixer.setTrackColor(trackNum, TrackColorCycle[nextIndex][1])
            else:
                mixer.setTrackColor(trackNum, DefaultTrackColor)
        else:
            mixer.setTrackColor(trackNum, TrackColorCycle[0][1])
