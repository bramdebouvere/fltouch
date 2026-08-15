import midi
import channels

from utilities.fl_class_import import FlMidiMsg
from behaviors.channel_banked_track_base_behavior import ChannelBankedTrackBaseBehavior
from device_hal import mcu_buttons
from utilities.track_banking_manager import TrackBankingManager
from device_hal.mcu_device import McuDevice
from constants.mcu_constants import FaderMax

class ChannelFaderBehavior(ChannelBankedTrackBaseBehavior):
    """Behavior for synchronizing MCU faders with channel-rack channel volumes."""

    def __init__(self, mcuDevice: McuDevice, trackBankingManager: TrackBankingManager):
        super().__init__(mcuDevice, trackBankingManager)

    def Update(self):
        """Update fader levels for all channels in the current bank."""
        for virtualIndex in self.TrackBanking.GetTrackIndexes():
            track = self.TrackBanking.GetHardwareTrack(virtualIndex)
            if track is None:
                continue

            level = 0
            if self.TrackBanking.VirtualTrackExists(virtualIndex):
                volume = channels.getChannelVolume(virtualIndex, False, True) # normalized 0.0 - 1.0, global index
                level = round(volume * FaderMax)

            track.fader.SetLevel(level, False)

    def OnMidiMsg(self, event: FlMidiMsg):
        # Fader touch selects the channel
        if self.__isFaderTouchEvent(event):
            return self.__handleFaderTouchEvent(event)

        # Fader slide sets the channel volume
        if self.__isFaderSlideEvent(event):
            return self.__handleFaderSlideEvent(event)

        return super().OnMidiMsg(event)

    def __isFaderTouchEvent(self, event: FlMidiMsg):
        return event.midiId == midi.MIDI_NOTEON and event.data2 > 0 and \
            mcu_buttons.Slider_1 <= event.data1 <= mcu_buttons.Slider_8

    def __handleFaderTouchEvent(self, event: FlMidiMsg):
        faderIndex = event.data1 - mcu_buttons.Slider_1
        virtualIndex = self.TrackBanking.GetTrackIndex(faderIndex)
        if virtualIndex != -1 and self.TrackBanking.VirtualTrackExists(virtualIndex):
            channels.selectOneChannel(virtualIndex, True)
        event.handled = True
        return event

    def __isFaderSlideEvent(self, event: FlMidiMsg):
        return event.midiId == midi.MIDI_PITCHBEND and event.midiChan < self.TrackBanking.TrackCount

    def __handleFaderSlideEvent(self, event: FlMidiMsg):
        virtualIndex = self.TrackBanking.GetTrackIndex(event.midiChan)
        if self.TrackBanking.VirtualTrackExists(virtualIndex):
            faderValue14 = event.data1 + (event.data2 << 7) # 14-bit fader value (0 - 16383)
            volume = max(0.0, min(1.0, faderValue14 / FaderMax))
            channels.setChannelVolume(virtualIndex, volume, useGlobalIndex=True)
        event.handled = True
        return event
