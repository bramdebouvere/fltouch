"""Builds and holds the virtual->real parameter map for the Channel Rack effect parameter view."""

import plugins

from constants.mcu_constants import MidiCcBlockStart

class _ChannelParamMapper:
    """
    Maps the hardware parameter view's virtual indexes onto a channel-rack generator's parameters.

    Similar to the Plugin mode's parameter mapper, but for generators. Plugins are addressed
    with the generator's channel index, using the global channel index.

    FL exposes a fixed 4240-parameter array for every wrapped VST: indexes 0-4095 are the VST parameters (the 
    plugin only uses the first N; the rest are unused placeholders with an empty name and an
    inert value), 4096-4223 are 128 MIDI-CC sends and 4224-4239 are 16 channel-aftertouch params. Banking
    through all of them would bury the user under hundreds of empty "0%" strips, so the map keeps only the
    generator's real parameters: indexes below the MIDI-CC block (MidiCcBlockStart) that have a non-empty
    name. Native FL generators and most VST3s report their true count (< MidiCcBlockStart, all named), so
    for them the cap is a no-op and name-filtering simply keeps their parameters.

    Virtual param index v (what the banking manager hands out, 0..len-1) maps to FL parameter index
    Map[v]. The map is built once when the parameter view opens a generator and only read afterwards, so
    the hot render path (which runs on every parameter value change) never rescans the parameter list.
    """

    def __init__(self):
        self._map = []

    @property
    def Map(self):
        """The virtual->real parameter index list. Map[v] is the FL parameter index for virtual param v."""
        return self._map

    def CreateMapForChannel(self, channel):
        """Build the map for the generator at the given global channel index. Returns an empty map when the channel is invalid."""
        # Non-plugin channels (e.g. automation clips) hold no plugin, so the SELECT flow then opens 
        # the editor but shows no parameters, like a sample or automation clip.
        if channel < 0 or not plugins.isValid(channel, -1, True):
            self._map = []
            return
        pluginName = plugins.getPluginName(channel, -1, False, True)
        print(f"Building parameter map for {pluginName} at channel {channel}")
        limit = min(plugins.getParamCount(channel, -1, True), MidiCcBlockStart)
        self._map = [p for p in range(limit) if plugins.getParamName(p, channel, -1, True).strip() != ''] # removes parameters with no name

# Singleton
ChannelParamMapper = _ChannelParamMapper()
