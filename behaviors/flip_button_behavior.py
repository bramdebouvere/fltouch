import midi
import mixer

from behaviors.mcu_base_behavior import McuBaseBehavior
from constants import mcu_constants
from device_hal import mcu_buttons
from utilities.button_manager import ButtonManager


class FlipButtonBehavior(McuBaseBehavior):
    """
    Flip: toggle effects on the active mixer track.
    Shift+Flip: toggle effects on all mixer tracks (all-or-nothing).
    """

    def OnMidiMsg(self, event):
        if event.midiId == midi.MIDI_NOTEON and event.data1 == mcu_buttons.Flip:
            if event.data2 > 0:
                if ButtonManager.ShiftPressed:
                    self._toggleAllTrackSlots()
                else:
                    self._toggleCurrentTrackSlots()
                event.handled = True
                return event
        return super().OnMidiMsg(event)

    def _toggleCurrentTrackSlots(self):
        track = mixer.trackNumber()
        print("Flipping all effects on/off for track %d" % track)
        # (value: -1 = toggle, 0 = disable, 1 = enable)
        mixer.enableTrackSlots(track, -1) # type: ignore
        mixer.afterRoutingChanged() # Makes sure the icon on the current track is visually updated

    def _toggleAllTrackSlots(self):
        print("Flipping all effects on/off for all tracks")
        count = mixer.trackCount()
        firstTrack = midi.TrackNum_Master + 1  # skip the master track
        any_enabled = any(mixer.isTrackSlotsEnabled(t) for t in range(firstTrack, count))
        enable = not any_enabled
        originalTrack = mixer.trackNumber()

        # FL Studio only repaints a track's FX-enable icon while that track is the
        # current mixer track (confirmed on the IL forum: afterRoutingChanged() alone
        # only refreshes the active track's icon). Briefly select each track to force
        # its icon to recompute, then restore whatever the user had selected.
        # Empty tracks have no icon to repaint (FL's own docs note enableTrackSlots
        # has "no visual indication" there), so skip the reselect for those. The
        # stored state still applies to any plugin added later.
        for t in range(firstTrack, count):
            mixer.enableTrackSlots(t, enable)
            if self._mixerTrackHasPlugin(t):
                mixer.setTrackNumber(t)

        mixer.setTrackNumber(originalTrack)
        mixer.afterRoutingChanged()

    def _mixerTrackHasPlugin(self, track):
        return any(mixer.isTrackPluginValid(track, slot) for slot in range(mcu_constants.EffectsSlotCount))
