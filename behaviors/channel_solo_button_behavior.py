import midi
import channels

from behaviors.channel_banked_track_base_behavior import ChannelBankedTrackBaseBehavior
from device_hal import mcu_buttons
from utilities.track_banking_manager import TrackBankingManager
from device_hal.mcu_device import McuDevice

class ChannelSoloButtonBehavior(ChannelBankedTrackBaseBehavior):
    """Behavior for handling SOLO button presses and LEDs based on channel-rack channel solo status."""

    def __init__(self, mcuDevice: McuDevice, trackBankingManager: TrackBankingManager):
        super().__init__(mcuDevice, trackBankingManager)

    def OnDisable(self):
        for track in self.McuDevice.tracks:
            if track is not None and track.buttons is not None:
                track.buttons.SetSoloButton(False)
        super().OnDisable()

    def Update(self):
        """Update all SOLO button LEDs to reflect current channel solo status."""
        for virtualIndex in self.TrackBanking.GetTrackIndexes():
            track = self.TrackBanking.GetHardwareTrack(virtualIndex)
            if track is not None and track.buttons is not None:
                isSolo = False
                if self.TrackBanking.VirtualTrackExists(virtualIndex):
                    isSolo = channels.isChannelSolo(virtualIndex, True)
                track.buttons.SetSoloButton(isSolo)

    def OnMidiMsg(self, event):
        """Handle SOLO button presses to solo/unsolo channels in the channel rack."""
        if event.midiId == midi.MIDI_NOTEON and event.data2 > 0:
            if mcu_buttons.Solo_1 <= event.data1 <= mcu_buttons.Solo_8:
                soloButtonIndex = event.data1 - mcu_buttons.Solo_1
                virtualIndex = self.TrackBanking.GetTrackIndex(soloButtonIndex)

                if self.TrackBanking.VirtualTrackExists(virtualIndex) and event.pmeFlags & midi.PME_System_Safe:
                    channels.soloChannel(virtualIndex, -1, True) # type: ignore ; -1 = toggle, True = global index

                event.handled = True
                return event

        return super().OnMidiMsg(event)
