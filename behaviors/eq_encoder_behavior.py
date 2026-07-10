import midi
import mixer

from utilities.fl_class_import import FlMidiMsg
from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal import mcu_buttons
from device_hal import mcu_knob_mode
from device_hal.mcu_device import McuDevice
from utilities.track_banking_manager import TrackBankingManager
from constants import eq_controls
from constants import mcu_encoder
from utilities.encoder_resolution import CalculateMixerEncoderRes, CalculateEncoderMovementDelta


class EqEncoderBehavior(McuBaseBehavior):
    """
    Controls the selected mixer track's built-in 3-band parametric EQ using the rotary encoders.

    The 9 EQ controls (3 bands x level/frequency/Q) are treated as virtual "tracks" handed out by the
    TrackBankingManager, so they spread across the main unit and any extenders and can be banked to
    when there are fewer than 9 encoders available.

    This does not extend MixerBankedTrackBaseBehavior: that base assumes a virtual index IS a mixer
    track, but here a virtual index is an EQ control of the (single) selected track. So the dirty/refresh
    bookkeeping is reimplemented to follow the selected track instead.
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
        """Called when the bank changes (e.g. banking buttons); refresh the rings immediately."""
        self.__needsUpdate = True
        self.Update()

    def OnDirtyMixerTrack(self, trackNum):
        # The EQ always targets the selected track, so refresh when that track (or all tracks) change
        if trackNum == -1 or trackNum == mixer.trackNumber():
            self.__needsUpdate = True

    def OnRefresh(self, flags):
        super().OnRefresh(flags)

        # A selection change retargets the EQ to a different track
        if flags & midi.HW_Dirty_Mixer_Sel:
            self.__needsUpdate = True

        if not self.__needsUpdate:
            return
        if not (flags & (midi.HW_Dirty_Mixer_Controls | midi.HW_Dirty_Mixer_Sel)):
            return

        self.Update()
        self.__needsUpdate = False

    def Update(self):
        """Update the encoder rings to reflect the selected track's EQ values."""
        baseEventId = mixer.getTrackPluginId(mixer.trackNumber(), 0)

        for virtualIndex in self.__trackBanking.GetTrackIndexes():
            track = self.__trackBanking.GetHardwareTrack(virtualIndex)
            if track is None or track.knob is None:
                continue

            if not self.__trackBanking.VirtualTrackExists(virtualIndex):
                # No EQ control assigned to this encoder -> all leds off
                track.knob.SetLedsValue(mcu_knob_mode.SingleDot, False, 0)
                continue

            eventId = eq_controls.GetEQControlEventID(baseEventId, virtualIndex)
            value = mixer.getEventValue(eventId, midi.MaxInt, False)
            ringMode = eq_controls.GetEQControlEncoderMode(virtualIndex)
            showCenter, ledValue = eq_controls.GetEQControlEncoderValue(virtualIndex, value)
            track.knob.SetLedsValue(ringMode, showCenter, ledValue)

        self.__needsUpdate = False

    def OnMidiMsg(self, event: FlMidiMsg):
        # Encoder click -> reset the control to its default (center)
        if event.midiId == midi.MIDI_NOTEON and event.data2 > 0:
            if event.data1 in [mcu_buttons.Encoder_1, mcu_buttons.Encoder_2, mcu_buttons.Encoder_3,
                               mcu_buttons.Encoder_4, mcu_buttons.Encoder_5, mcu_buttons.Encoder_6,
                               mcu_buttons.Encoder_7, mcu_buttons.Encoder_8]:
                encoderIndex = event.data1 - mcu_buttons.Encoder_1
                virtualIndex = self.__trackBanking.GetTrackIndex(encoderIndex)
                if self.__trackBanking.VirtualTrackExists(virtualIndex):
                    baseEventId = mixer.getTrackPluginId(mixer.trackNumber(), 0)
                    eventId = eq_controls.GetEQControlEventID(baseEventId, virtualIndex)
                    self.__resetControl(virtualIndex, eventId)
                event.handled = True
                return event

        if event.midiId != midi.MIDI_CONTROLCHANGE:
            return super().OnMidiMsg(event)
        if event.midiChan != 0:
            return super().OnMidiMsg(event)

        # Encoder rotation: data1 = EncoderCcBase + encoder index, data2 = relative rotation value
        if mcu_encoder.EncoderCcBase <= event.data1 <= mcu_encoder.EncoderCcLast:
            encoderIndex = event.data1 - mcu_encoder.EncoderCcBase

            event.inEv = event.data2
            event.outEv = CalculateEncoderMovementDelta(event.data2)

            if encoderIndex < self.__trackBanking.TrackCount:
                virtualIndex = self.__trackBanking.GetTrackIndex(encoderIndex)
                if not self.__trackBanking.VirtualTrackExists(virtualIndex):
                    return super().OnMidiMsg(event)

                baseEventId = mixer.getTrackPluginId(mixer.trackNumber(), 0)
                eventId = eq_controls.GetEQControlEventID(baseEventId, virtualIndex)
                Res = CalculateMixerEncoderRes(event.outEv)
                mixer.automateEvent(eventId, event.outEv, midi.REC_Controller, 0, 1, Res)

            event.handled = True
            return event

        return super().OnMidiMsg(event)

    def __resetControl(self, index, eventId):
        """Reset a control to its EQ default (per-control normalized value, or center as a fallback)."""
        value = eq_controls.GetEQControlResetValue(index)
        if value is None:
            value = midi.FromMIDI_Max >> 1  # fall back to center until the real default is filled in
        mixer.automateEvent(eventId, value, midi.REC_MIDIController, 0)
