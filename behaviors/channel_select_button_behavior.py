import midi
import channels

from modes.mcu_composite_mode import McuCompositeMode
from behaviors.channel_banked_track_base_behavior import ChannelBankedTrackBaseBehavior
from device_hal import mcu_buttons
from utilities.track_banking_manager import TrackBankingManager
from device_hal.mcu_device import McuDevice
from utilities.channel_param_mapper import ChannelParamMapper
from utilities.channel_rack_mode_state import PARAMS

class ChannelSelectButtonBehavior(ChannelBankedTrackBaseBehavior):
    """
    Handles SELECT buttons in the Channel Rack overview.

    The SELECT LED lights for the currently selected channel. On press: selects the channel, opens its
    generator window and if the generator exposes editable parameters, it switches to the parameter view.
    Channels with no editable parameters (e.g. some audio-clip channels) just open and stay in overview.
    """

    def __init__(self, mcuDevice: McuDevice, trackBankingManager: TrackBankingManager, compositeMode: McuCompositeMode):
        super().__init__(mcuDevice, trackBankingManager)
        self._compositeMode = compositeMode

    def OnDisable(self):
        for track in self.McuDevice.tracks:
            if track is not None and track.buttons is not None:
                track.buttons.SetSelectButton(False)
        super().OnDisable()

    def Update(self):
        """Update all SELECT button LEDs to reflect the currently selected channel."""
        for virtualIndex in self.TrackBanking.GetTrackIndexes():
            track = self.TrackBanking.GetHardwareTrack(virtualIndex)
            if track is not None and track.buttons is not None:
                isSelected = False
                if self.TrackBanking.VirtualTrackExists(virtualIndex):
                    isSelected = channels.isChannelSelected(virtualIndex, True)
                track.buttons.SetSelectButton(isSelected)

    def OnMidiMsg(self, event):
        if not (event.midiId == midi.MIDI_NOTEON and event.data2 > 0 and
                mcu_buttons.Select_1 <= event.data1 <= mcu_buttons.Select_8):
            return super().OnMidiMsg(event)

        hardwareIndex = event.data1 - mcu_buttons.Select_1
        virtualIndex = self.TrackBanking.GetTrackIndex(hardwareIndex)

        if virtualIndex == -1 or not self.TrackBanking.VirtualTrackExists(virtualIndex):
            event.handled = True
            return event

        # only when it is safe to call FL functions
        if event.pmeFlags & midi.PME_System_Safe:
            # Before we select the channel, look if it is already selected
            alreadySelected = channels.isChannelSelected(virtualIndex, True)

            # Select the channel
            channels.selectOneChannel(virtualIndex, True)

            ChannelParamMapper.CreateMapForChannel(virtualIndex)
            if len(ChannelParamMapper.Map) > 0:
                # Generator with real params: open its window and switch to the parameter view. The
                # window is closed again when we return to the overview (see McuChannelRackMode.OnModeSwitch).
                channels.showCSForm(virtualIndex, 1, True) # 1 = show
                channels.focusEditor(virtualIndex, True)
                self._compositeMode.SwitchTo(PARAMS)
            else:
                # No editable params (for example sample / automation clip): Stay in the overview.
                # Selecting a new channel always shows its editor.
                # Pressing SELECT on the channel that was already selected
                # toggles it, so a second press on the same channel hides it.
                channels.showCSForm(virtualIndex, -1 if alreadySelected else 1, True) # -1 = toggle, 1 = show

        event.handled = True
        return event
