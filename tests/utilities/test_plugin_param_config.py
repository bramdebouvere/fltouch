import contextlib
import io
import json
import os
import tempfile
import unittest
from unittest.mock import patch

from utilities.plugin_param_config import _PluginParamConfig

def _write_config(directory, fileName, content):
    with open(os.path.join(directory, fileName), 'w', encoding='utf-8') as file:
        if isinstance(content, str):
            file.write(content)
        else:
            json.dump(content, file)

class TestPluginParamConfigLoading(unittest.TestCase):
    """Exercises _Load() against real temp directories/files on disk."""

    def test_missing_config_folder_returns_no_configs(self):
        missingDir = os.path.join(tempfile.gettempdir(), 'fltouch_test_missing_plugin_param_configs')
        with patch('utilities.plugin_param_config._CONFIG_DIR', missingDir):
            config = _PluginParamConfig()

        self.assertEqual(config.GetOrderedIndexes('Anything', [0, 1, 2]), [0, 1, 2])
        self.assertIsNone(config.GetColor('Anything', 0))

    def test_loads_valid_config_file(self):
        with tempfile.TemporaryDirectory() as tempDir:
            _write_config(tempDir, 'foo.json', {
                'pluginName': 'Foo',
                'parameters': [{'index': 2}, {'index': 0, 'color': '#FF0000'}],
            })
            with patch('utilities.plugin_param_config._CONFIG_DIR', tempDir):
                config = _PluginParamConfig()

        self.assertEqual(config.GetOrderedIndexes('Foo', [0, 1, 2]), [2, 0, 1])
        self.assertEqual(config.GetColor('Foo', 0), 0xFF0000)
        self.assertIsNone(config.GetColor('Foo', 1))

    def test_skips_malformed_json_without_crashing(self):
        with tempfile.TemporaryDirectory() as tempDir:
            _write_config(tempDir, 'broken.json', '{not valid json')
            _write_config(tempDir, 'good.json', {'pluginName': 'Good', 'parameters': []})
            with patch('utilities.plugin_param_config._CONFIG_DIR', tempDir):
                config = _PluginParamConfig()

        self.assertEqual(config.GetOrderedIndexes('Good', [3, 4]), [3, 4])
        self.assertEqual(config.GetOrderedIndexes('Broken', [3, 4]), [3, 4])

    def test_skips_json_missing_pluginname(self):
        with tempfile.TemporaryDirectory() as tempDir:
            _write_config(tempDir, 'nokey.json', {'parameters': []})
            with patch('utilities.plugin_param_config._CONFIG_DIR', tempDir):
                config = _PluginParamConfig()

        self.assertEqual(config.GetOrderedIndexes('Whatever', [1]), [1])

    def test_ignores_non_json_files(self):
        with tempfile.TemporaryDirectory() as tempDir:
            _write_config(tempDir, 'notes.txt', 'this is not a config')
            with patch('utilities.plugin_param_config._CONFIG_DIR', tempDir):
                config = _PluginParamConfig()

        self.assertEqual(config.GetOrderedIndexes('Whatever', [1]), [1])

class TestPluginParamConfigLogic(unittest.TestCase):
    """Exercises GetOrderedIndexes/GetColor/DumpCurrentParameterList against an in-memory config, skipping the filesystem."""

    def _configFor(self, configs):
        config = _PluginParamConfig()
        config._configs = configs
        return config

    def test_orders_configured_params_first_then_appends_leftovers(self):
        config = self._configFor({'Foo': {'pluginName': 'Foo', 'parameters': [{'index': 5}, {'index': 2}]}})
        self.assertEqual(config.GetOrderedIndexes('Foo', [0, 1, 2, 3, 4, 5]), [5, 2, 0, 1, 3, 4])

    def test_ignores_stale_index_not_present_on_plugin(self):
        config = self._configFor({'Foo': {'pluginName': 'Foo', 'parameters': [{'index': 99}, {'index': 1}]}})
        self.assertEqual(config.GetOrderedIndexes('Foo', [0, 1, 2]), [1, 0, 2])

    def test_dedups_repeated_index_in_config(self):
        config = self._configFor({'Foo': {'pluginName': 'Foo', 'parameters': [{'index': 1}, {'index': 1}]}})
        self.assertEqual(config.GetOrderedIndexes('Foo', [0, 1, 2]), [1, 0, 2])

    def test_unconfigured_plugin_keeps_natural_order(self):
        config = self._configFor({'Foo': {'pluginName': 'Foo', 'parameters': [{'index': 1}]}})
        self.assertEqual(config.GetOrderedIndexes('OtherPlugin', [0, 1, 2]), [0, 1, 2])

    def test_get_color_parses_hex_string(self):
        config = self._configFor({'Foo': {'pluginName': 'Foo', 'parameters': [{'index': 3, 'color': '#00CCFF'}]}})
        self.assertEqual(config.GetColor('Foo', 3), 0x00CCFF)

    def test_get_color_none_when_param_has_no_color(self):
        config = self._configFor({'Foo': {'pluginName': 'Foo', 'parameters': [{'index': 3}]}})
        self.assertIsNone(config.GetColor('Foo', 3))

    def test_get_color_none_for_invalid_hex(self):
        config = self._configFor({'Foo': {'pluginName': 'Foo', 'parameters': [{'index': 3, 'color': 'not-a-color'}]}})
        self.assertIsNone(config.GetColor('Foo', 3))

    def test_get_color_none_for_unconfigured_plugin(self):
        config = self._configFor({})
        self.assertIsNone(config.GetColor('Foo', 3))

    def test_dump_current_parameter_list_prints_expected_schema(self):
        config = self._configFor({})
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            config.DumpCurrentParameterList('Foo', [(0, 'Mix', None), (1, 'Time', 0xFF8800)])

        # Output is bracketed with "--- ... ---" marker lines around the JSON; strip them before parsing.
        lines = buffer.getvalue().splitlines()
        dumped = json.loads('\n'.join(lines[1:-1]))
        self.assertEqual(dumped, {
            'pluginName': 'Foo',
            'parameters': [
                {'index': 0, 'name': 'Mix'},
                {'index': 1, 'name': 'Time', 'color': '#FF8800'},
            ],
        })

if __name__ == '__main__':
    unittest.main()
