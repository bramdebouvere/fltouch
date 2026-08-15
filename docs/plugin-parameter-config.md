# Custom Plugin Parameter Config

By default, when you open a plugin in [Effects Mode](modes.md#effects-mode) or
[Channels Mode](modes.md#channels-mode-channel-rack), its parameters are shown in whatever order
FL Studio reports them in, with no particular color. This feature lets you override that per
plugin: pick which parameters show up, in what order, and what color each one gets on the
scribble strip.

This works identically whether the parameters belong to an FX plugin (Effects Mode) or a Channel
Rack generator (Channels Mode).

## Where config files live

Config files are `.json` files inside the `plugin_param_configs/` folder, next to the script
files. Every `.json` file in that folder is loaded automatically when the script starts. The
filename itself doesn't matter, only the `pluginName` field inside each file does.

## File format

```json
{
  "pluginName": "Fruity parametric EQ 2",
  "parameters": [
    { "index": 0, "name": "Band 1 level", "color": "#94359F" },
    { "index": 7, "name": "Band 1 freq",  "color": "#94359F" },
    { "index": 35, "name": "Main level" }
  ]
}
```

- **`pluginName`**: must match the plugin's name exactly as FL Studio reports it.
- **`index`**: the plugin's real FL Studio parameter index. Required.
- **`name`**: purely for your own reference while editing the file; the script ignores it and
  always shows the plugin's real parameter name on the hardware.
- **`color`** (optional): a `#RRGGBB` hex color for that parameter's scribble strip. Leave it out
  to leave that strip at its default (white).

Reordering the entries in `parameters` reorders how they're banked across the 8 hardware encoders.
Any of the plugin's parameters you *don't* list are appended afterward, in FL Studio's natural
order. So a config only needs to cover the parameters you actually want to reorder or color; you
don't have to list every single one. If a listed `index` no longer exists on the plugin (e.g. after
a plugin update), it's silently ignored.

## Building a config for a new plugin

1. Open the plugin as usual. Press **Select** on its FX slot (Effects Mode) or its channel
   (Channels Mode), so you're looking at its parameter view.
2. Press **Shift + Record 1** (the Record/Arm button under the first strip). This prints a
   ready-to-edit JSON block for that plugin's current parameters to FL Studio's script output
   console:
   ```
   --- PLUGIN PARAMETER DUMP for .json file ---
   { "pluginName": "...", "parameters": [ ... ] }
   --- END PARAMETER DUMP ---
   ```
3. Copy that JSON out of the console, reorder the `parameters` entries into whatever order you
   want them banked in, and add `"color"` fields to any you'd like to color-code.
4. Save it as a new `.json` file inside `plugin_param_configs/` (any filename works).
5. Restart FL Studio so the new config is picked up.

A few example configs ship with the script that you can use as a reference.
