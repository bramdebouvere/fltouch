import sys
import types
import unittest

# ChannelParamMapper imports the FL Studio 'plugins' module at import time. FL modules aren't available
# in a plain Python test environment, so we stub it before importing the module under test. Individual tests
# then swap in a FakePlugins with controlled parameter data.
if 'plugins' not in sys.modules:
    sys.modules['plugins'] = types.ModuleType('plugins')

import utilities.channel_param_mapper as mapper_module
from utilities.channel_param_mapper import ChannelParamMapper
from constants.mcu_constants import MidiCcBlockStart

class FakePlugins:
    """Minimal stub for the FL 'plugins' module driving the channel-rack (index, slotIndex=-1) form."""

    def __init__(self, paramNames, valid=True):
        self._paramNames = paramNames
        self._valid = valid

    def isValid(self, index, slotIndex=-1, useGlobalIndex=False):
        return self._valid

    def getPluginName(self, index, slotIndex=-1, userName=False, useGlobalIndex=False):
        return 'FakeGenerator'

    def getParamCount(self, index, slotIndex=-1, useGlobalIndex=False):
        return len(self._paramNames)

    def getParamName(self, paramIndex, index, slotIndex=-1, useGlobalIndex=False):
        return self._paramNames[paramIndex]

class TestChannelParamMapper(unittest.TestCase):

    def _useParams(self, paramNames):
        mapper_module.plugins = FakePlugins(paramNames)

    def test_keeps_only_named_params(self):
        # Unnamed / whitespace-only params are dropped (they are the VST's unused placeholder slots).
        self._useParams(['Cutoff', '', 'Resonance', '   ', 'Envelope'])
        ChannelParamMapper.CreateMapForChannel(0)
        self.assertEqual(ChannelParamMapper.Map, [0, 2, 4])

    def test_negative_channel_yields_empty_map(self):
        self._useParams(['A', 'B'])
        ChannelParamMapper.CreateMapForChannel(-1)
        self.assertEqual(ChannelParamMapper.Map, [])

    def test_empty_plugin_yields_empty_map(self):
        self._useParams([])
        ChannelParamMapper.CreateMapForChannel(0)
        self.assertEqual(ChannelParamMapper.Map, [])

    def test_invalid_channel_yields_empty_map(self):
        # A non-plugin channel (e.g. an automation clip) is not a valid plugin: the map is empty and the
        # plugin.* accessors are never reached (they would raise "Plugin not valid" in FL Studio).
        class ExplodingPlugins(FakePlugins):
            def getPluginName(self, index, slotIndex=-1, userName=False, useGlobalIndex=False):
                raise AssertionError('plugin accessor called for an invalid channel')

            def getParamCount(self, index, slotIndex=-1, useGlobalIndex=False):
                raise AssertionError('plugin accessor called for an invalid channel')

        mapper_module.plugins = ExplodingPlugins(['A', 'B'], valid=False)
        ChannelParamMapper.CreateMapForChannel(0)
        self.assertEqual(ChannelParamMapper.Map, [])

    def test_caps_at_midi_cc_block(self):
        # Wrapped VSTs report a fixed 4240-slot array; only indexes below MidiCcBlockStart are real params.
        self._useParams(['p'] * (MidiCcBlockStart + 200))
        ChannelParamMapper.CreateMapForChannel(3)
        self.assertEqual(len(ChannelParamMapper.Map), MidiCcBlockStart)
        self.assertEqual(ChannelParamMapper.Map[-1], MidiCcBlockStart - 1)

    def test_uses_global_channel_index(self):
        # Every plugins call must pass useGlobalIndex=True (the last positional arg).
        calls = []

        class RecordingPlugins(FakePlugins):
            def getParamCount(self, index, slotIndex=-1, useGlobalIndex=False):
                calls.append(('count', slotIndex, useGlobalIndex))
                return len(self._paramNames)

            def getParamName(self, paramIndex, index, slotIndex=-1, useGlobalIndex=False):
                calls.append(('name', slotIndex, useGlobalIndex))
                return self._paramNames[paramIndex]

        mapper_module.plugins = RecordingPlugins(['A', 'B'])
        ChannelParamMapper.CreateMapForChannel(5)
        self.assertTrue(all(slotIndex == -1 and useGlobalIndex is True for _, slotIndex, useGlobalIndex in calls))


if __name__ == '__main__':
    unittest.main()
