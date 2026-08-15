import device
import midi
import transport
import mixer
from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal import mcu_buttons
from utilities.button_manager import ButtonManager


class TrackMarkerBehavior(McuBaseBehavior):
    """Handles Move, Link Channel, Marker, AddMarker buttons."""

    def __init__(self, mcuDevice):
        super().__init__(mcuDevice)

    def OnMidiMsg(self, event):
        if event.midiId == midi.MIDI_NOTEON and event.data1 in [
            mcu_buttons.Move,
            mcu_buttons.LinkChannel,
            mcu_buttons.Marker,
            mcu_buttons.AddMarker,
        ]:
            btn = event.data1
            # Move and Marker can act as jog sources
            if btn in [mcu_buttons.Move, mcu_buttons.Marker]:
                if event.data2 == 0:
                    if ButtonManager.JogSource == btn:
                        ButtonManager.JogSource = 0
                else:
                    ButtonManager.JogSource = btn

            elif btn == mcu_buttons.AddMarker:
                if event.data2 > 0:
                    transport.globalTransport(
                        midi.FPT_AddMarker + int(ButtonManager.ShiftPressed),
                        2,
                        event.pmeFlags,
                    )

            elif btn == mcu_buttons.LinkChannel:
                if event.data2 > 0 and event.pmeFlags & midi.PME_System_Safe:
                    if ButtonManager.ShiftPressed:
                        mixer.linkTrackToChannel(midi.ROUTE_StartingFromThis)
                    else:
                        mixer.linkTrackToChannel(midi.ROUTE_ToThis)

            device.directFeedback(event)
            event.handled = True
            return event

        return super().OnMidiMsg(event)
