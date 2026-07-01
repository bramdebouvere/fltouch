import midi
import mixer

from utilities.fl_class_import import FlMidiMsg
from behaviors.mixer_banked_track_base_bahavior import MixerBankedTrackBaseBehavior
from behaviors.mcu_mixer_screen_behavior import McuMixerScreenBehavior
from device_hal import mcu_buttons
from device_hal import mcu_knob_mode
from utilities.track_banking_manager import TrackBankingManager
from device_hal.mcu_device import McuDevice
from constants import mcu_encoder
from utilities.encoder_resolution import CalculateMixerEncoderRes, CalculateEncoderMovementDelta


class MixerEncoderSendsBehavior(MixerBankedTrackBaseBehavior):
    """
    Behavior for controlling the sends from the selected mixer track to the banked tracks using the rotary encoders.

    The source is always the currently selected track (mixer.trackNumber()).
    Each encoder targets a banked destination track.
    * Turning an encoder sets the send level (enabling the route first if it was not yet active). 
    * Clicking an encoder toggles the send route on/off.
    """

    def __init__(self, mcuDevice: McuDevice, trackBankingManager: TrackBankingManager, screenBehavior: McuMixerScreenBehavior):
        # Because the sends always reflect the selected (source) track, this reacts to selection changes
        # (HW_Dirty_Mixer_Sel) in addition to the usual mixer control changes.
        super().__init__(mcuDevice, trackBankingManager, midi.HW_Dirty_Mixer_Controls | midi.HW_Dirty_Mixer_Sel)
        self.__screenBehavior = screenBehavior

    def OnDirtyMixerTrack(self, trackNum):
        """
        Mark for refresh on changes to the selected (source) track. Needed for when a send level changes in FL Studio
        and needs to be shown on the device.

        The send levels live on the source track's plugin space, and the source may be banked away from
        the currently visible tracks. The base class only tracks dirty tracks that are in the current bank,
        so forward a dirty event for the source track as an 'all tracks' (-1) change to force a refresh.
        """
        if trackNum == mixer.trackNumber():
            trackNum = -1
        super().OnDirtyMixerTrack(trackNum)

    def Update(self):
        """
        Called from the base class when the track bank changes, the selection changes or tracks are marked dirty.
        Updates the encoder rings to reflect the send level from the selected track to each banked track.
        """
        sourceTrack = mixer.trackNumber()
        sourceBaseId = mixer.getTrackPluginId(sourceTrack, 0)

        for virtualIndex in self.TrackBanking.GetTrackIndexes():
            track = self.TrackBanking.GetHardwareTrack(virtualIndex)

            if track is None or track.knob is None:
                continue

            if not self.TrackBanking.VirtualTrackExists(virtualIndex):
                # Empty slot: all leds off
                track.knob.SetLedsValue(mcu_knob_mode.SingleDot, False, 0)
                continue

            if mixer.getRouteSendActive(sourceTrack, virtualIndex) == 0:
                # No send route to this track: ring dark
                track.knob.SetLedsValue(mcu_knob_mode.Wrap, False, 0)
                continue

            sendEventId = sourceBaseId + midi.REC_Mixer_Send_First + virtualIndex  # type: ignore
            sendValue = mixer.getEventValue(sendEventId, midi.MaxInt, False)

            # Convert FL Studio send value (0-FromMIDI_Max) to a wrap-style fill (0-11)
            ledValue = round(sendValue * (mcu_encoder.LedWrapMax / midi.FromMIDI_Max))
            track.knob.SetLedsValue(mcu_knob_mode.Wrap, False, ledValue)

    def OnMidiMsg(self, event: FlMidiMsg):
        """Handle MIDI events for the send encoders (click = toggle route, turn = set level)."""

        # Handle encoder click to toggle the send route on/off
        if event.midiId == midi.MIDI_NOTEON and event.data2 > 0:
            if event.data1 in [mcu_buttons.Encoder_1, mcu_buttons.Encoder_2, mcu_buttons.Encoder_3,
                               mcu_buttons.Encoder_4, mcu_buttons.Encoder_5, mcu_buttons.Encoder_6,
                               mcu_buttons.Encoder_7, mcu_buttons.Encoder_8]:
                encoderIndex = event.data1 - mcu_buttons.Encoder_1
                virtualIndex = self.TrackBanking.GetTrackIndex(encoderIndex)
                if self.TrackBanking.VirtualTrackExists(virtualIndex) and (event.pmeFlags & midi.PME_System_Safe):
                    self.__toggleRoute(virtualIndex)
                event.handled = True
                return event

        if event.midiId != midi.MIDI_CONTROLCHANGE:
            return super().OnMidiMsg(event)

        if event.midiChan != 0:
            return super().OnMidiMsg(event)

        # Handle encoder rotation (CC messages for encoders)
        # Encoder data format: data1 = 0x10 + encoder index, data2 = rotation value
        if mcu_encoder.EncoderCcBase <= event.data1 <= mcu_encoder.EncoderCcLast:
            encoderIndex = event.data1 - mcu_encoder.EncoderCcBase

            event.inEv = event.data2
            event.outEv = CalculateEncoderMovementDelta(event.data2)

            if encoderIndex < self.TrackBanking.TrackCount:
                virtualIndex = self.TrackBanking.GetTrackIndex(encoderIndex)
                if not self.TrackBanking.VirtualTrackExists(virtualIndex):
                    return super().OnMidiMsg(event)

                sourceTrack = mixer.trackNumber()

                # If there is no send route yet, enable it first so the level can be dialed in
                if mixer.getRouteSendActive(sourceTrack, virtualIndex) == 0:
                    if not (event.pmeFlags & midi.PME_System_Safe):
                        event.handled = True
                        return event
                    if mixer.setRouteTo(sourceTrack, virtualIndex, -1) < 0: # type: ignore (does return a value, not documented)
                        self.__screenBehavior.OnSendTempMsg('Cannot send to this track')
                        event.handled = True
                        return event
                    mixer.afterRoutingChanged()

                sendEventId = mixer.getTrackPluginId(sourceTrack, 0) + midi.REC_Mixer_Send_First + virtualIndex  # type: ignore
                Res = CalculateMixerEncoderRes(event.outEv)
                mixer.automateEvent(sendEventId, event.outEv, midi.REC_Controller, 0, 1, Res)

            event.handled = True
            return event

        return super().OnMidiMsg(event)

    def __toggleRoute(self, destIndex):
        """Toggle the send route from the selected track to the given destination track."""
        if mixer.setRouteTo(mixer.trackNumber(), destIndex, -1) < 0: # type: ignore (does return a value, not documented)
            self.__screenBehavior.OnSendTempMsg('Cannot send to this track')
        else:
            mixer.afterRoutingChanged()
            self.Update()
