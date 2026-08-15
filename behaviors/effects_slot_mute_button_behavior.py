import midi
import mixer

from utilities.fl_class_import import FlMidiMsg
from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal import mcu_buttons
from device_hal.mcu_device import McuDevice
from utilities.track_banking_manager import TrackBankingManager

class EffectsSlotMuteButtonBehavior(McuBaseBehavior):
    """
    Mutes/bypasses the selected mixer track's effect slots with the per-strip MUTE buttons.

    A virtual index handed out by the TrackBankingManager is an effect slot (0-9) of the selected track.
    The slot's enabled state is the REC_Plug_Mute event: it reads high when the slot is enabled/active
    and low when muted (confirmed on hardware). The MUTE LED is therefore lit when the slot is NOT
    enabled. Like EqEncoderBehavior, this targets the selected track rather than treating the virtual
    index as a mixer track.
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

        # Turn off all mute LEDs
        for hardwareIndex in range(self.__trackBanking.GetHardwareTrackCount()):
            track = self.McuDevice.GetTrack(hardwareIndex)
            if track is not None and track.buttons is not None:
                track.buttons.SetMuteButton(False)
        super().OnDisable()

    def __onTrackBankChange(self, newFirstTrack):
        self.__needsUpdate = True
        self.Update()

    def OnDirtyMixerTrack(self, trackNum):
        if trackNum == -1 or trackNum == mixer.trackNumber():
            self.__needsUpdate = True

    def OnRefresh(self, flags):
        super().OnRefresh(flags)

        if flags & midi.HW_Dirty_Mixer_Sel:
            self.__needsUpdate = True

        if not self.__needsUpdate:
            return
        if not (flags & (midi.HW_Dirty_Mixer_Controls | midi.HW_Dirty_Mixer_Sel)):
            return

        self.Update()
        self.__needsUpdate = False

    def __muteEventId(self, track, slot):
        return mixer.getTrackPluginId(track, slot) + midi.REC_Plug_Mute  # type: ignore

    def __isSlotEnabled(self, track, slot):
        # REC_Plug_Mute reads high when the slot is enabled/active, low when muted.
        value = mixer.getEventValue(self.__muteEventId(track, slot), midi.MaxInt, False)
        return value > (midi.FromMIDI_Max >> 1)  # type: ignore

    def Update(self):
        """Update each MUTE LED: lit when the slot is muted (off for empty/enabled slots)."""
        track = mixer.trackNumber()

        for virtualIndex in self.__trackBanking.GetTrackIndexes():
            hwTrack = self.__trackBanking.GetHardwareTrack(virtualIndex)
            if hwTrack is None or hwTrack.buttons is None:
                continue

            isMuted = False
            if self.__trackBanking.VirtualTrackExists(virtualIndex) and mixer.isTrackPluginValid(track, virtualIndex):
                isMuted = not self.__isSlotEnabled(track, virtualIndex)
            hwTrack.buttons.SetMuteButton(isMuted)

        self.__needsUpdate = False

    def OnMidiMsg(self, event: FlMidiMsg):
        if event.midiId == midi.MIDI_NOTEON and event.data2 > 0:
            if mcu_buttons.Mute_1 <= event.data1 <= mcu_buttons.Mute_8:
                muteButtonIndex = event.data1 - mcu_buttons.Mute_1
                virtualIndex = self.__trackBanking.GetTrackIndex(muteButtonIndex)
                track = mixer.trackNumber()

                if (self.__trackBanking.VirtualTrackExists(virtualIndex)
                        and mixer.isTrackPluginValid(track, virtualIndex)
                        and event.pmeFlags & midi.PME_System_Safe):
                    eventId = self.__muteEventId(track, virtualIndex)
                    # Toggle: if currently enabled, mute it (0); otherwise enable it (max).
                    newValue = 0 if self.__isSlotEnabled(track, virtualIndex) else midi.FromMIDI_Max
                    mixer.automateEvent(eventId, newValue, midi.REC_MIDIController, 0)
                    
                event.handled = True
                return event

        return super().OnMidiMsg(event)
