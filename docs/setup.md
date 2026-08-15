# Setup & Configuration

This page covers getting the hardware talking to FL Studio, installing the script and the settings you can
customize in `settings.py`.

## 1. Put your device(s) into MCU mode

The X-Touch and X-Touch Extender both need to be switched from their default "Standalone" mode
into **MCU (Mackie Control Universal) mode** before FL Studio can talk to them. Do this once per
device:

1. Make sure the unit is turned **off**.
2. Hold down the **SELECT** button on channel strip 1.
3. While still holding SELECT, power the unit on.
4. Turn **encoder 1** until the display reads `MC`.
5. Turn **encoder 2** to pick the interface you're connecting through (e.g. `USB`).
6. Press the channel-1 **SELECT** button again to confirm.
7. The unit will finish booting normally.

For a version of these steps with photos, see *"Step 3: Getting started"* in
[the official Behringer quick-start guide](https://cdn-media.empowertribe.com/5f4ebaa5746d48b39c2bc317641de448/QSG_BE_0808-AAD_X-TOUCH_WW.pdf)
(p. 13), or [this walkthrough by Zizzer Productions](https://www.zizzerproductions.com/post/make-behringer-universal-control-surface-work-with-fl-studio).

If you have one or more X-Touch Extenders, put each of them into MCU mode the same way.

## 2. Install the script files

1. Download this repository (**Code → Download ZIP** on [the fltouch GitHub page](https://github.com/bramdebouvere/fltouch)).
2. Copy everything inside the ZIP's `fltouch-main` folder into a new subfolder of your FL Studio
   Scripts folder. This repository *is* that subfolder — the finished path should look like:
   - Windows: `%UserProfile%\Documents\Image-Line\Data\FL Studio\Settings\Hardware\fltouch`
   - macOS: `~/Image-Line/FL Studio/Settings/Hardware/fltouch`

*Note: it's strongly advised to use this script with the **latest version of FL Studio**. Older versions may or may not work.*

## 3. Tell FL Studio about each device

Open FL Studio's **Options → MIDI Settings**. You'll see one entry per physical device (your
X-Touch, and one per Extender).

For each device:
- Set the **controller type** dropdown to `FLtouch X-Touch` (for the main unit) or
  `FLtouch X-Touch Extender` (for each extender).
- Set the **port/channel** number: `102` for the main X-Touch, then `103`, `104`, ... for each
  extender.

![FL Studio Midi Settings Screen](https://user-images.githubusercontent.com/3641681/161856471-97810569-0ed5-4123-968a-68a11d295be2.png)

## 4. Configure `settings.py`

`settings.py` sits in the same folder as the script files. Open it in any text editor to change
either of the two settings below, then **restart FL Studio** for your changes to take effect.

### Extender position

If you have one or more X-Touch Extenders, `ExtenderPosition` tells the script where they sit
relative to the main unit, so track banking lines up with what's physically in front of you:

| Setting | Physical layout | Meaning |
|---|---|---|
| `mcu_extender_location.Left` | `EEEM` (extenders, then main unit) | All extenders sit to the **left** of the main unit |
| `mcu_extender_location.Right` | `MEEE` (main unit, then extenders) | All extenders sit to the **right** of the main unit |
| `mcu_extender_location.Middle` | `EMEE` | One extender sits to the **left** of the main unit, and any remaining extenders sit to its **right** |

```python
ExtenderPosition = mcu_extender_location.Middle
```

All connected units act as one wide contiguous strip of channels — e.g. a main unit plus one
extender shows/controls 16 channels at a time instead of 8, and the [banking buttons](button-reference.md#track-banking)
move the whole combined array together.

> **Important:** whatever layout you pick, physically power your extenders on **in left-to-right
> order** — FL Studio needs to see them in that order to assign the right one to the right slot.

### Footswitch actions

The X-Touch has two rear-panel pedal jacks, **Foot SW 1** and **Foot SW 2**. Each can be assigned
one of four actions independently:

| Setting | What pressing the pedal does |
|---|---|
| `footswitch_action.TogglePlay` | Start playback; press again to stop (same as the **Play** button) |
| `footswitch_action.ToggleRecord` | Turn recording on; press again to turn it off (same as the **Record** button) |
| `footswitch_action.ToggleMetronome` | Turn the metronome on/off |
| `footswitch_action.Passthrough` | Do nothing in the script, so you can map the pedal yourself in FL Studio |

```python
FootswitchAction1 = footswitch_action.TogglePlay     # Foot SW 1
FootswitchAction2 = footswitch_action.ToggleRecord   # Foot SW 2
```

These are the defaults the script ships with — change either line to whichever action you'd
rather have on that jack.

## 5. Printable overlay (optional)

Bobby-Funk has made a printable overlay (which is now slightly changed for the V2) for the controller's function labels. Print it
15.7956 cm / 6.21875 inches wide on A4 paper:

<img width="1194" height="1338" alt="Printable X-Touch overlay" src="https://github.com/user-attachments/assets/4348e560-4b87-4ae2-90d4-27f00ec10172" />

---

Once everything above is done, head to [getting started](getting-started.md) for a quick
first-time walkthrough and the full control reference.
