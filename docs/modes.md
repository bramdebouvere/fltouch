# Modes

The 6 modes are selected with the encoder-assign row, in the hardware's physical left-to-right
order: **Pan, Stereo, EQ, Sends, Effects, Channels** (named "Inst" on the unit itself). Only
one mode is active at a time, and switching modes completely repurposes the 8 faders, 8 encoders,
scribble strips, meters, and the Rec/Solo/Mute/Select button rows.

Across every mode, pressing the button of the mode that's *already* active resets that mode's
[track banking](button-reference.md#track-banking) back to the first bank rather than doing
nothing — handy if you've lost track of where you banked to.

Some modes have a [Menu](getting-started.md#menu), opened and closed with the **Menu / Flip** button.

## Pan Mode

Press **Pan** (display shows `Pn`). A general-purpose mixer overview.

| Control | Behavior |
|---|---|
| Faders 1-8 | Volume of the 8 banked mixer tracks. Touching a fader selects that track. |
| Encoders 1-8 (turn) | Pan of the corresponding track. |
| Encoders 1-8 (click) | Reset that track's pan to center. |
| Scribble strips | Track number (top), track name (bottom), tinted with the track's FL Studio color. |
| Meters | Live peak meters for the 8 banked tracks. |
| Rec/Solo/Mute/Select | Arm, solo, mute, and select each banked track (Select also focuses FL's Mixer window). |
| Name/Value | Rename the selected track. **Shift+Name/Value**: cycle the track's color (Red → Yellow → Green → Cyan → Blue → Purple → back to FL's default gray). |
| Plugin Picker | Opens FL's plugin picker to add an effect to the selected track. |
| Jog wheel | Works normally (see [Jog Wheel & Jog Sources](button-reference.md#jog-wheel--jog-sources)). |
| Flip → Menu | `FxSlots` (toggle all FX slots on this track), `ALLFxSl` (toggle FX slots on every track), `Rev Pol` (toggle phase/polarity), `Swap LR` (toggle left/right channel swap) — each shows its current on/off state. |

## Stereo Mode

Press **Stereo** (display shows `St`). Identical to Pan Mode except the encoders control stereo
width instead of pan.

| Control | Behavior |
|---|---|
| Encoders 1-8 (turn) | Stereo separation of the corresponding track (wide ↔ mono). |
| Encoders 1-8 (click) | Reset that track's stereo separation to center. |
| Everything else | Identical to [Pan Mode](#pan-mode): faders, scribble strips, meters, Rec/Solo/Mute/Select, Name/Value, Plugin Picker, jog wheel, and the Menu are all the same. |

## EQ Mode

Press **EQ** (display shows `Eq`). Controls the *currently selected mixer track's* built-in 3-band
parametric EQ.

The EQ has 9 controls in total — 3 per band (Low shelf, Peak/mid, High shelf) × 3 parameters
(Level, Frequency, Q) — spread across the 8 encoders, so use
[banking](button-reference.md#track-banking) to reach the 9th.

| Control | Behavior |
|---|---|
| Encoders (turn) | Adjust the corresponding band/parameter. |
| Encoders (click) | Reset that one control to its default: 0 dB for any Level, ~0.27 Q for any Q, and 90 Hz / 1500 Hz / 8000 Hz for the Low/Peak/High frequency respectively. |
| Scribble strips | Each control's short label (e.g. `LowLvl`, `PeakFrq`, `HighQ`) and live value, colored by band: yellow (low), green (peak), cyan (high). |

The encoder ring for a Q control fills up **backwards** compared to a Level control: a high Q is a
narrow, surgical band, so it's shown with fewer LEDs lit, while a low (wide) Q shows more.

## Sends Mode

Press **Sends** (display shows `SE`). Controls how much of the *currently selected* track's
signal is sent to another track.

| Control | Behavior |
|---|---|
| Faders 1-8 | Volume of the banked tracks (same as Pan/Stereo Mode). |
| Encoders 1-8 (turn) | Send level from the selected track to the corresponding banked destination track. If no send route exists yet, turning the encoder creates one automatically. If FL Studio can't create the route (e.g. it would cause a feedback loop), the screen briefly shows "Cannot send to this track" instead. |
| Encoders 1-8 (click) | Toggle that send route on/off without changing the level. |
| Scribble strips, meters, Rec/Solo/Mute/Select, Name/Value, Smooth, jog wheel, Flip → Menu | Same as [Pan Mode](#pan-mode). |

## Effects Mode

Press **Effects** (display shows `Ef`). Browses and edits the effect plugins loaded on the *currently selected mixer track*. This mode has two layers plus a Menu, navigated like so:

- **Slot overview** (the default) → press **Select** on a loaded slot → **Parameter view**
- **Parameter view** → press **Select** → back to **Slot overview**
- **Parameter view** → press **Flip** → **Menu**
- **Menu** → press **Flip** again → back to **Parameter view**

### Slot overview (the default view)

The track's 10 effect slots, spread across the 8 encoders (bank to see the rest).

| Control | Behavior |
|---|---|
| Encoders (turn) | That slot's dry/wet mix level. |
| Encoders (click) | Reset that slot's mix to 100% wet. |
| Mute buttons | Bypass/un-bypass that individual effect. |
| Scribble strips | Slot number (top), plugin name or `<empty>` (bottom), tinted with the plugin's own FX-slot color. |
| Select LEDs | Only lit for slots that actually hold a plugin. |
| Select button | On a populated slot: opens that plugin and switches to the parameter view below. |
| Plugin Picker | Opens FL's plugin picker to load an effect into a slot. |

### Parameter view (opened via Select on a loaded slot)

Locks onto the plugin you opened.

| Control | Behavior |
|---|---|
| Encoders (turn) | Adjust the mapped parameter. Only the plugin's real, named parameters are shown — unused/placeholder slots are skipped. |
| Encoders (click) | Revert that parameter to the value it had the moment you opened the plugin. |
| Scribble strips | Parameter name (top) and live value (bottom). Order and colors can be customized per plugin — see [Custom Plugin Parameter Config](plugin-parameter-config.md). |
| Select button (any) | Return to the slot overview (closes the plugin's window on the main unit). |
| Name/Value | Rename the plugin. **Shift+Name/Value**: cycle the FX slot's color (requires FL Studio 2026 / scripting API v41 or newer — older versions show a message asking you to update FL Studio instead). |
| Flip | Open the Menu. |

### Menu (opened via Flip from the parameter view)

| Item | Action |
|---|---|
| `<Preset` | Step the open plugin to its previous saved preset. |
| `Preset>` | Step the open plugin to its next saved preset. |

Press **Flip** again to return to the parameter view.

## Channels Mode (Channel Rack)

Press **Channels** (silkscreened "Free" on the hardware; display shows `Ch`). This fully replaces
the old manual "Free" MIDI-link mode with full Channel Rack control. Also shows/focuses FL
Studio's Channel Rack window. Structured the same way as Effects Mode — overview, parameter view,
Menu:

- **Channel overview** (the default) → press **Select** on a generator with parameters → **Parameter view**
- **Parameter view** → press **Select** → back to **Channel overview**
- **Parameter view** → press **Flip** → **Menu**
- **Menu** → press **Flip** again → back to **Parameter view**

### Channel overview (the default view)

| Control | Behavior |
|---|---|
| Faders 1-8 | Volume of the 8 banked channels. Touching a fader selects that channel. |
| Encoders 1-8 (turn) | Pan of the corresponding channel. |
| Encoders 1-8 (click) | Reset that channel's pan to center. |
| Mute / Solo buttons | Mute / solo that channel. |
| Scribble strips | Channel number (top), channel name (bottom), tinted with the channel's color. |
| Select button | Selects the channel and opens its generator. If the generator has editable parameters, this also switches to the parameter view below; if it doesn't (e.g. an audio/automation clip channel), it just shows/hides the generator's own window. |
| Plugin Picker | Opens FL's plugin picker to add a new generator. |
| Name/Value | Rename the selected generator. **Shift+Name/Value**: cycle the channel's color. |
| Jog wheel | Works normally, same as the mixer overview modes. |

### Parameter view (opened via Select on a generator)

Locks onto the generator's channel you opened.

| Control | Behavior |
|---|---|
| Encoders (turn) | Adjust the mapped parameter (real, named parameters only, same filtering as Effects Mode). |
| Encoders (click) | Revert that parameter to the value it had the moment you opened the generator. |
| Scribble strips | Parameter name/value, with the same optional custom order/color config as Effects Mode — see [Custom Plugin Parameter Config](plugin-parameter-config.md). |
| Faders | Suppressed — touching one doesn't select anything here. |
| Select button (any) | Return to the channel overview (closes the generator's window). |
| Name/Value | Rename the generator. **Shift+Name/Value**: cycle the channel's color. |
| Flip | Open the Menu. |

### Menu (opened via Flip from the parameter view)

This is the richest Menu of any mode — it also covers the "assign to mixer track" feature:

| Item | Action |
|---|---|
| `<Preset` | Step the open generator to its previous saved preset. |
| `Preset>` | Step the open generator to its next saved preset. |
| `AsToSel` | Route this generator's audio output to the **currently selected mixer track**. Bottom row shows the current target track number, or `---` if unassigned. |
| `AsToFre` | Route this generator's audio output to the **first mixer track with no plugins that isn't already targeted by another channel**. Shows "No free mixer track available" if every track is taken. Bottom row shows the current target, same as `AsToSel`. |

Press **Flip** again to return to the parameter view.
