# Button Reference

This page documents every physical control, organized by section, with what a plain press does and what changes when
you hold **Shift**. Controls whose meaning depends on the active [mode](modes.md) are marked as
such.

If a term below (Menu, Jog source, Track banking...) isn't obvious, check the
[Core Concepts](getting-started.md#core-concepts) section first.


## Mode / Encoder-Assign Buttons

| Button | Press | Press while already active |
|---|---|---|
| Pan | Enter [Pan Mode](modes.md#pan-mode) | Reset that mode's [track banking](#track-banking) |
| Stereo | Enter [Stereo Mode](modes.md#stereo-mode) | Same |
| EQ | Enter [EQ Mode](modes.md#eq-mode) | Same |
| Sends | Enter [Sends Mode](modes.md#sends-mode) | Same |
| Effects | Enter [Effects Mode](modes.md#effects-mode) | Same |
| Channels (labeled "Instr") | Enter [Channels Mode](modes.md#channels-mode-channel-rack) | Same |

Only one mode's LED is lit at a time, and the 2-character assignment display shows an abbreviation
of the active mode (`Pn`, `St`, `Eq`, `SE`, `Ef`, `Ch`).

## Window / Time Row

| Button | Press | Notes |
|---|---|---|
| Browser | Show & focus the Browser | LED reflects whether the Browser is focused |
| Main | Show & focus the Playlist | LED reflects whether the Playlist is focused |
| Window | Becomes a [jog source](#jog-wheel--jog-sources) | — |
| In | Set the punch-in point | LED stays lit until Out is pressed |
| Out | Set the punch-out point | Clears the In LED |
| Select | Toggle punch mode | Clears the In LED |

## Plugin Picker

Opens FL Studio's plugin picker, to add an effect (mixer modes) or a generator (Channels mode)

## Menu

Opens/closes the current mode's [Menu](getting-started.md#menu) with extra functions, if there is one.
See [Modes](modes.md) for what's in each mode's Menu (EQ Mode has none).

## Jog Wheel & Jog Sources

The wheel itself just sends a rotation delta — what that delta *does* depends on which button (if
any) currently controls it, called its **jog source**. Holding one of these buttons claims the wheel
for that purpose; releasing it (except Move/Marker, which simply take over from whatever else was
active) hands the wheel back to its default behavior.

| Source | Turning the wheel... | Shift changes... |
|---|---|---|
| *(none held)* | If the Browser is focused: browse it. Otherwise shows the Playlist and seeks the song position (fine seek if [Scrub](#misc--status-leds) is toggled on) | While scrubbing, seeking is **10× coarser without Shift**, and **fine/precise with Shift held** |
| Mixer | Selects the next/previous mixer track, showing its name, and focuses the Mixer | — |
| Channels | Selects the next/previous Channel Rack channel, showing its name, and focuses the Channel Rack | — |
| Tempo | Adjusts the project tempo, showing the new BPM | — |
| Free 1-4 | Emits a generic MIDI CC event for you to link manually to anything in FL Studio ("Link to controller") | — |
| Move | Moves the current selection | — |
| Marker | Jumps between markers | With Shift: selects a range between markers instead of jumping |
| Undo (F7, held) | Steps through Undo history, showing the current level on screen | — |
| Zoom | Zooms the timeline horizontally | With Shift: zooms the other axis instead |
| Window | Cycles through open FL Studio windows, showing the newly-focused window's name | — |
| Pattern | Selects the next/previous pattern, showing its name, and focuses the Playlist | — |

## F1-F8 Row

| Button | Press | Shift + press |
|---|---|---|
| Cut (F1) | Cut | Sends FL's generic F1 function (Help) |
| Copy (F2) | Copy | Sends FL's generic F2 function (Pattern Color) |
| Paste (F3) | Paste | Sends FL's generic F3 function (Windows Menu) |
| Insert (F4) | Insert | Sends FL's generic F4 function (New Pattern) |
| Delete (F5) | Delete | Sends FL's generic F5 function (Playlist) |
| Item Menu (F6) | Open the context menu for the focused item | Sends FL's generic F6 function (Channel Rack) |
| Undo (F7) | Becomes a [jog source](#jog-wheel--jog-sources) — hold it and turn the jog wheel to step through Undo history | Sends FL's generic F7 function (Piano roll) (does not become a jog source when shifted) |
| Undo/Redo (F8) | Triggers one Undo step directly | Sends FL's generic F8 function (Plugin picker) |

The Shift-held actions are FL Studio's own generic F-key transport bindings — whatever you've
bound them to in FL Studio, independent of this script.

## Transport

Always active, regardless of mode.

| Button | Press | Shift + press |
|---|---|---|
| Rewind | Rewind | Plays back at **0.5×** speed while held; releasing either button restores 1× |
| Fast Forward | Fast-forward | Plays back at **2×** speed while held; releasing either button restores 1× |
| Stop | Stop playback (LED lit while stopped) | — |
| Play | Start/toggle playback (LED flashes with the beat) | — |
| Record | Toggle recording (LED reflects recording state) | — |
| Song/Loop | Toggle Song vs. Pattern loop mode | — |
| Metronome | Toggle FL Studio's metronome | Toggle the **device's own** audible click instead |
| Countdown | Toggle recording count-in/precount | — |
| Snap | Toggle Snap on/off | Open/cycle the Snap-mode selector instead of toggling |
| Shift | Modifier — see the rest of this page for what it changes | n/a |
| Edison | Open the Edison audio editor, recording the selected mixer track | — |
| Mode | Sends a generic transport command; not currently mapped to a distinct feature (behaves like Record) | — |


## Channel-Strip Buttons (Rec/Solo/Mute/Select)

The 4 rows of 8 buttons above each fader are fully mode-dependent — see the relevant mode in
[Modes](modes.md) for exactly what they do:

| Row | Pan / Stereo / Sends | EQ | Effects (slot overview) | Effects (parameter view) | Channels (overview) | Channels (parameter view) |
|---|---|---|---|---|---|---|
| Record/Arm | Arm/unarm the track | inactive | inactive | Shift+Record 1 dumps the open plugin's parameters as JSON (see [Custom Plugin Parameter Config](plugin-parameter-config.md)) | inactive | Shift+Record 1 dumps the open generator's parameters as JSON |
| Solo | Solo/unsolo the track | inactive | inactive | inactive | Solo/unsolo the channel | inactive |
| Mute | Mute/unmute the track | inactive | Bypass that effect slot | inactive | Mute/unmute the channel | inactive |
| Select | Select the track, focus the Mixer | inactive | Open a populated slot's plugin | Return to slot overview | Select the channel, open its generator | Return to channel overview |

## Encoders

Turning and clicking each of the 8 encoders means something different in every mode — see
[Modes](modes.md) for the full breakdown (Pan/Stereo pan or stereo width, Sends send levels, EQ's
9 bands, Effects/Channel Rack mix levels or plugin parameters). As a rule of thumb across every
mode: **turning adjusts a value, clicking resets it** (either to center/default, or to the value
it had when you opened whatever you're editing).

## Faders

| Fader | Touch | Slide |
|---|---|---|
| 1-8 (Pan/Stereo/Sends/Effects slot overview) | Selects that mixer track | Sets that track's volume, or (Effects) that slot's dry/wet mix — see [Modes](modes.md) |
| 1-8 (Channels overview) | Selects that channel | Sets that channel's volume |
| 1-8 (EQ mode, any parameter view) | Does nothing (touch note is swallowed) | Passes through as raw MIDI — you can manually MIDI-link these faders to something else in FL Studio while in these modes |
| 9 ("Main") | — | **Always** controls FL Studio's master volume, in every mode |

## Track Banking

Active in every mode, always targeting whatever the current mode/view is displaying (mixer
tracks, FX slots, EQ bands, plugin parameters, or Channel Rack channels).

| Button | Action |
|---|---|
| Fader Bank Left | Jump the visible 8 items left by a full bank of 8 |
| Fader Bank Right | Jump the visible 8 items right by a full bank of 8 |
| Fader Channel Left | Shift the visible items left by 1 |
| Fader Channel Right | Shift the visible items right by 1 |

## Marker / Track Row

| Button | Press | Shift + press |
|---|---|---|
| Move | Becomes a [jog source](#jog-wheel--jog-sources) (move current selection) | — |
| Link Channel | Link the current mixer track to the selected Channel Rack channel | Link starting from this track outward, instead of just to it |
| Marker | Becomes a jog source (jump between markers) | Becomes a jog source for marker *selection* instead of jumping |
| Add Marker | Add a marker at the current position | Add the alternate marker variant (e.g. with a name prompt, depending on FL Studio's own behavior) |

## System Buttons

| Button | Press | Shift + press |
|---|---|---|
| Save | Save the project | Save As |
| Menu | Open FL Studio's main/context menu | — |
| Escape | Escape/close the current dialog | Answer **No** to a dialog |
| Enter | Confirm/accept | Answer **Yes** to a dialog |
| Time Format | Toggle the time display between Bars:Beats and Min:Sec/SMPTE | — |

## Name/Value

Renames whatever's selected, or with Shift, cycles its color. Exact target depends on the active
mode — see [Modes](modes.md):

| Mode | Press | Shift + press |
|---|---|---|
| Pan / Stereo / Sends | Rename the selected mixer track | Cycle the track's color |
| Effects (parameter view) | Rename the open plugin | Cycle the FX slot's color (needs FL Studio 2026 / scripting API v41+) |
| Channels (overview & parameter view) | Rename the selected generator | Cycle the channel's color |
| EQ | Not active | — |

The color cycle always runs the same order: Red → Yellow → Green → Cyan → Blue → Purple → back to
FL Studio's default gray.

## Footswitches

The two rear-panel pedal jacks are independently configurable in `settings.py` — see
[Setup & Configuration](setup.md#footswitch-actions). Out of the box: **Foot SW 1** toggles
playback, **Foot SW 2** toggles recording.

## Misc / Status LEDs

| Control | Purpose |
|---|---|
| Scrub | Toggles scrub mode for the default jog wheel behavior (see [Jog Wheel & Jog Sources](#jog-wheel--jog-sources)) |
| SMPTE / Beats LEDs | Reflect the current time-display format — not user-pressable |
| Rude Solo LED | Lit whenever any mixer track is soloed — not user-pressable |
