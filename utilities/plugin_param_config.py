
import json
import os

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # go up 2 levels from the current file
_CONFIG_DIR = os.path.join(_PROJECT_ROOT, 'plugin_param_configs')

class _PluginParamConfig:
    """
    Loads a configuration file for a plugin that allows reordering and coloring the parameters,
    from plugin_param_configs/.

    Each config is a JSON file holding one plugin's "pluginName" and a "parameters" list of
    {"index": realFLParamIndex, "name": <informational, ignored on load>, "color": "#RRGGBB" (optional)}.
    Parameters not listed in a plugin's config are appended on the end, using FL's existing order.
    A configured index that no longer exists on the plugin is ignored.

    All configs are loaded at import time.
    """

    def __init__(self):
        self._configs = self._Load()

    def _Load(self):
        configs = {}
        if not os.path.isdir(_CONFIG_DIR):
            return configs

        for fileName in os.listdir(_CONFIG_DIR):
            if not fileName.lower().endswith('.json'):
                continue
            filePath = os.path.join(_CONFIG_DIR, fileName)
            try:
                with open(filePath, 'r', encoding='utf-8') as file:
                    config = json.load(file)
                pluginName = config['pluginName']
            except (OSError, ValueError, KeyError) as e:
                print(f"Skipping invalid plugin param config '{fileName}': {e}")
                continue
            configs[pluginName] = config

        return configs

    def GetOrderedIndexes(self, pluginName: str, visibleParameterIndexes: list[int]) -> list[int]:
        """
        Reorders visibleParameterIndexes according to the plugin's config: configured parameters first (in file order),
        then any remaining parameters appended afterwards in their natural order. Returns visibleParameterIndexes
        unchanged if no config exists for pluginName.
        """
        config = self._configs.get(pluginName)
        if config is None:
            return visibleParameterIndexes

        visibleSet = set(visibleParameterIndexes)
        configured: list[int] = []
        for param in config.get('parameters', []):
            index = param.get('index')
            if index in visibleSet and index not in configured:
                configured.append(index)

        leftover = [index for index in visibleParameterIndexes if index not in configured]
        return configured + leftover

    def GetColor(self, pluginName: str, index: int) -> int | None:
        """Returns the configured RGB int color for a plugin's parameter, or None if not configured."""
        config = self._configs.get(pluginName)
        if config is None:
            return None

        for param in config.get('parameters', []):
            if param.get('index') == index:
                color = param.get('color')
                if not color:
                    return None
                try:
                    return int(color.lstrip('#'), 16)
                except ValueError:
                    return None

        return None

    def DumpCurrentParameterList(self, pluginName: str, entries: list[tuple[int, str, int | None]]) -> None:
        """
        Prints a ready-to-paste config JSON for pluginName's currently banked parameters, so a new
        config file can be made by copying this output, reordering entries and adding colors.
        """
        parameters = []
        for index, paramName, existingColor in entries:
            parameter = {'index': index, 'name': paramName}
            if existingColor is not None:
                parameter['color'] = f'#{existingColor:06X}'
            parameters.append(parameter)

        dump = {'pluginName': pluginName, 'parameters': parameters}
        print(f"--- PLUGIN PARAMETER DUMP for .json file ---")
        print(json.dumps(dump, indent=2))
        print('--- END PARAMETER DUMP ---')

# Singleton
PluginParamConfig = _PluginParamConfig()
