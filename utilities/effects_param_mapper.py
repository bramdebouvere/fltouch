"""Builds and holds the virtual->real parameter map for the Effects parameter view."""

import mixer
import plugins

from constants.mcu_constants import MidiCcBlockStart

class _EffectsParamMapper:
    """
    Maps the hardware's parameter view's virtual indexes onto a plugin's real, named parameters.

    FL exposes a fixed 4240-parameter array for every wrapped VST: indexes 0-4095 are the VST parameter
    slots (the plugin only uses the first N; the rest are unused placeholders with an empty name and an
    inert value), 4096-4223 are 128 MIDI-CC sends and 4224-4239 are 16 channel-aftertouch params. Banking
    through all of them would bury the user under hundreds of empty "0%" strips, so the map keeps only the
    plugin's real parameters: indexes below the MIDI-CC block (MidiCcBlockStart) that have a non-empty
    name. Native FL plugins and most VST3s report their true count (< MidiCcBlockStart, all named), so for
    them the cap is a no-op and name-filtering simply keeps their parameters.

    Virtual param index v (what the banking manager hands out, 0..len-1) maps to FL parameter index
    Map[v]. The map is built once when the parameter view opens a plugin and only read afterwards, so the
    hot render path (which runs on every parameter value change) never rescans the parameter list.
    """

    def __init__(self):
        self._map = []

    @property
    def Map(self):
        """The virtual->real parameter index list. Map[v] is the FL parameter index for virtual param v."""
        return self._map

    def CreateMapForPlugin(self, track, slot):
        """Build the map for the plugin at (track, slot). Yields an empty map for an invalid slot."""
        if track < 0 or slot < 0 or not mixer.isTrackPluginValid(track, slot):
            self._map = []
            return
        pluginName = plugins.getPluginName(track, slot)
        print(f"Building parameter map for {pluginName} at ({track}, {slot})")
        limit = min(plugins.getParamCount(track, slot), MidiCcBlockStart)
        self._map = [p for p in range(limit) if plugins.getParamName(p, track, slot).strip() != ''] # removes parameters with no name

# Singleton
EffectsParamMapper = _EffectsParamMapper()
