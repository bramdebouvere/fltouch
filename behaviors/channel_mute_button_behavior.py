import midi
import channels

from behaviors.channel_banked_track_base_behavior import ChannelBankedTrackBaseBehavior
from device_hal import mcu_buttons
from utilities.track_banking_manager import TrackBankingManager
from device_hal.mcu_device import McuDevice

class ChannelMuteButtonBehavior(ChannelBankedTrackBaseBehavior):
    """Behavior for handling MUTE button presses and LEDs based on channel-rack channel mute status."""

    def __init__(self, mcuDevice: McuDevice, trackBankingManager: TrackBankingManager):
        super().__init__(mcuDevice, trackBankingManager)

    def OnDisable(self):
        for track in self.McuDevice.tracks:
            if track is not None and track.buttons is not None:
                track.buttons.SetMuteButton(False)
        super().OnDisable()

    def Update(self):
        """Update all MUTE button LEDs to reflect current channel mute status."""
        for virtualIndex in self.TrackBanking.GetTrackIndexes():
            track = self.TrackBanking.GetHardwareTrack(virtualIndex)
            if track is not None and track.buttons is not None:
                isMuted = False
                if self.TrackBanking.VirtualTrackExists(virtualIndex):
                    isMuted = channels.isChannelMuted(virtualIndex, True)
                track.buttons.SetMuteButton(isMuted)

    def OnMidiMsg(self, event):
        """Handle MUTE button presses to mute/unmute channels in the channel rack."""
        if event.midiId == midi.MIDI_NOTEON and event.data2 > 0:
            if mcu_buttons.Mute_1 <= event.data1 <= mcu_buttons.Mute_8:
                muteButtonIndex = event.data1 - mcu_buttons.Mute_1
                virtualIndex = self.TrackBanking.GetTrackIndex(muteButtonIndex)

                if self.TrackBanking.VirtualTrackExists(virtualIndex) and event.pmeFlags & midi.PME_System_Safe:
                    channels.muteChannel(virtualIndex, -1, True) # -1 = toggle

                event.handled = True
                return event

        return super().OnMidiMsg(event)
