import midi
import mixer

from utilities.fl_class_import import FlMidiMsg
from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal import mcu_buttons
from device_hal import mcu_knob_mode
from device_hal.mcu_device import McuDevice
from utilities.track_banking_manager import TrackBankingManager
from constants import mcu_encoder
from utilities.encoder_resolution import CalculateMixerEncoderRes, CalculateEncoderMovementDelta

class EffectsSlotEncoderBehavior(McuBaseBehavior):
    """
    Controls the per-slot mix (dry/wet) level of the selected mixer track's effect slots with the rotary
    encoders.

    A virtual index handed out by the TrackBankingManager is an effect slot (0-9) of the selected track,
    so the slots spread across the unit and bank like the EQ controls do. This mirrors EqEncoderBehavior
    rather than extending MixerBankedTrackBaseBehavior (a virtual index is a slot, not a mixer track).
    """

    def __init__(self, mcuDevice: McuDevice, trackBankingManager: TrackBankingManager):
        super().__init__(mcuDevice)
        self.__trackBanking = trackBankingManager
        self.__needsUpdate = False

    def OnEnable(self):
        super().OnEnable()
        self.__trackBanking.AddTrackChangeSubscriber(self.__onTrackBankChange)
        self.__needsUpdate = True
        self.Update()

    def OnDisable(self):
        self.__trackBanking.RemoveTrackChangeSubscriber(self.__onTrackBankChange)
        self.McuDevice.ClearEncoderRings()
        super().OnDisable()

    def __onTrackBankChange(self, newFirstTrack):
        self.__needsUpdate = True
        self.Update()

    def OnDirtyMixerTrack(self, trackNum):
        # The slots always belong to the selected track, so refresh when it (or all tracks) change.
        if trackNum == -1 or trackNum == mixer.trackNumber():
            self.__needsUpdate = True

    def OnRefresh(self, flags):
        super().OnRefresh(flags)

        # A selection change retargets the slots to a different track.
        if flags & midi.HW_Dirty_Mixer_Sel:
            self.__needsUpdate = True

        if not self.__needsUpdate:
            return
        if not (flags & (midi.HW_Dirty_Mixer_Controls | midi.HW_Dirty_Mixer_Sel)):
            return

        self.Update()
        self.__needsUpdate = False

    def Update(self):
        """Update the encoder rings to reflect each slot's mix level (off for empty slots)."""
        track = mixer.trackNumber()

        for virtualIndex in self.__trackBanking.GetTrackIndexes():
            hwTrack = self.__trackBanking.GetHardwareTrack(virtualIndex)
            if hwTrack is None or hwTrack.knob is None:
                continue

            if not self.__trackBanking.VirtualTrackExists(virtualIndex) or not mixer.isTrackPluginValid(track, virtualIndex):
                hwTrack.knob.SetLedsValue(mcu_knob_mode.SingleDot, False, 0)
                continue

            eventId = mixer.getTrackPluginId(track, virtualIndex) + midi.REC_Plug_MixLevel  # type: ignore
            value = mixer.getEventValue(eventId, midi.MaxInt, False)
            fraction = value / midi.FromMIDI_Max  # type: ignore
            ledValue = max(0, min(mcu_encoder.LedWrapMax, round(fraction * mcu_encoder.LedWrapMax)))
            hwTrack.knob.SetLedsValue(mcu_knob_mode.Wrap, False, ledValue)

        self.__needsUpdate = False

    def OnMidiMsg(self, event: FlMidiMsg):
        # Encoder click -> reset the slot's mix level to full (100% wet)
        if event.midiId == midi.MIDI_NOTEON and event.data2 > 0:
            if mcu_buttons.Encoder_1 <= event.data1 <= mcu_buttons.Encoder_8:
                encoderIndex = event.data1 - mcu_buttons.Encoder_1
                virtualIndex = self.__trackBanking.GetTrackIndex(encoderIndex)
                track = mixer.trackNumber()
                if self.__trackBanking.VirtualTrackExists(virtualIndex) and mixer.isTrackPluginValid(track, virtualIndex):
                    eventId = mixer.getTrackPluginId(track, virtualIndex) + midi.REC_Plug_MixLevel  # type: ignore
                    mixer.automateEvent(eventId, midi.FromMIDI_Max, midi.REC_MIDIController, 0)
                event.handled = True
                return event

        if event.midiId != midi.MIDI_CONTROLCHANGE:
            return super().OnMidiMsg(event)
        if event.midiChan != 0:
            return super().OnMidiMsg(event)

        # Encoder rotation: data1 = 0x10 + encoder index, data2 = relative rotation value
        if mcu_encoder.EncoderCcBase <= event.data1 <= mcu_encoder.EncoderCcLast:
            encoderIndex = event.data1 - mcu_encoder.EncoderCcBase

            outEv = CalculateEncoderMovementDelta(event.data2)

            virtualIndex = self.__trackBanking.GetTrackIndex(encoderIndex)
            track = mixer.trackNumber()
            if self.__trackBanking.VirtualTrackExists(virtualIndex) and mixer.isTrackPluginValid(track, virtualIndex):
                eventId = mixer.getTrackPluginId(track, virtualIndex) + midi.REC_Plug_MixLevel  # type: ignore
                Res = CalculateMixerEncoderRes(outEv)
                mixer.automateEvent(eventId, outEv, midi.REC_Controller, 0, 1, Res)

            event.handled = True
            return event

        return super().OnMidiMsg(event)
