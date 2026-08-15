# Getting Started

## Core concepts

A handful of ideas come up constantly across every mode. Understanding these five first makes the
rest of the documentation much easier to follow.

### Modes

The X-Touch has 6 **modes**, one active at a time, selected with the 6 buttons in the encoder-assign
row: **Pan, Stereo, EQ, Sends, Effects, Channels** (the "Channels" button is silkscreened "Inst" on
the hardware). Switching modes completely repurposes every fader, encoder, scribble strip and
per-channel button. See [Modes](modes.md) for what each one does.

Pressing the button for the mode that's *already* active resets that
mode's [track banking](#track-banking) back to the first bank.

### Track banking

Each hardware unit shows 8 channel strips at a time. **Banking** pages through whatever the
current mode is displaying (mixer tracks, effect slots, EQ bands, plugin parameters, or Channel
Rack channels) 8 at a time, using the Bank Left/Right and Channel Left/Right buttons.
If you have an Extender attached, it extends the amount of channels rather than showing something
different (see [Setup & Configuration](setup.md#extender-position)).

### Shift

The **Shift** button doesn't do anything by itself. It's a modifier, like on a computer keyboard.
Holding it changes what many other buttons do. 
See the [Button Reference](button-reference.md) to find out how holding shift can give some buttons
other functions.

### Jog source

The jog wheel is reused for many different jobs (scrubbing, zooming, stepping through markers,
adjusting tempo, browsing patterns...). Which job it's currently doing is called its **jog
source**.

A handful of buttons (Move, Marker, Zoom, Window, Pattern, Mixer, Channels, Tempo, Free
1-4, and Undo) each claim the jog wheel for their own purpose while pressed; if nothing has claimed
it, turning the wheel scrubs/seeks the playlist instead. See the
[jog wheel section](button-reference.md#jog-wheel--jog-sources) for the full list.

### Menu

Some modes have mode-specific functions (e.g. stepping a plugin's presets, or toggling a track's polarity)
that don't fit on the normal fader/encoder controls. Press **Flip** (or **Menu**) to open it, and press it
again to close it and return to what you were doing.

The Menu stays open across other button presses until you explicitly close it or switch modes.
Each mode's Menu contents are listed in [Modes](modes.md).

## Your first 5 minutes

A quick tour to get a feel for the controller. This assumes [setup](setup.md) is already done and
you have an FL Studio project open with a few tracks and at least one effect on a track.

1. **Press the Pan button.** Its LED lights up and the small display reads `Pn` — you're now in
   [Pan mode](modes.md#pan-mode).
2. **Touch fader 1**, then slide it. Touching it selects that mixer track (FL Studio's Mixer
   window jumps to it); sliding it changes the track's volume.
3. **Turn encoder 1.** It adjusts that same track's pan; the LED ring around it shows the pan
   position. **Press the encoder in** — it snaps back to center.
4. **Press Flip/Menu.** A [Menu](#menu) appears with a few track utilities (`FxSlots`, `ALLFxSl`,
   `Rev Pol`, `Swap LR`). Press **Flip/Menu** again to close it.
5. **Press Fader Bank Right**, then **Fader Bank Left** to see the
   banking move to the next 8 tracks and back.
6. **Turn the jog wheel** with nothing else held down — it scrubs the playlist position. **Press Scrub** for finer control.
7. **Press Effects.** You're now looking at the selected track's 10 effect slots. **Press Select**
   under a slot that has a plugin loaded — you've jumped into that plugin's parameters. Turn an
   encoder to change a parameter, then **press Select** again to go back to the slot list.
8. **Press Plugin Picker / Global View** to open the plugin picker. Use the **arrows** to go trough the plugins and select one to **insert using the Middle button** in the arrows, or using the **Enter** button.
9. **Press Channels** (labeled "Inst" on the hardware) to see the Channel Rack's generators
   instead — same select-to-open, select-to-go-back pattern as Effects.

From here, [Modes](modes.md) covers each of the 6 modes in full detail, and
[Button Reference](button-reference.md) is the complete lookup table for every control.
