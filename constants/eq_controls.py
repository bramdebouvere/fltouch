import midi

from device_hal import mcu_knob_mode

# Shared definitions for the 9 controls of the mixer's built-in 3-band parametric EQ.
#
# A "virtual track index" (0-8) handed out by the TrackBankingManager indexes straight into the
# EQ_CONTROLS list below, which is the single source of truth for both the encoder and the screen
# behavior. The controls are grouped by shelf so each band's three controls stay adjacent:
#
#   index : 0       1       2     3        4        5      6        7        8
#           LowLvl  LowFrq  LowQ  PeakLvl  PeakFrq  PeakQ  HighLvl  HighFrq  HighQ
#           band 0 (low shelf)    band 1 (peaking)         band 2 (high shelf)

# Parameter types. The value is also the offset added to the band within the EQ event-id block
# (e.g. baseEventId + REC_Mixer_EQ_Gain + band).
Gain = 0  # level
Freq = 1  # frequency
Q = 2     # width / slope

# RGB values will be mapped by mcu_colors.GetMcuColor to the intended MCU screen color.
_CYAN = 0x478C8D
_GREEN = 0x00FF00
_YELLOW = 0xFFC000

# Reset defaults, as a normalized fraction (0.0 - 1.0) of each parameter's range, captured from FL
# Studio. A click resets the control to this value (applied as round(fraction * midi.FromMIDI_Max)).
_GAIN_DEFAULT = 0.5                      # 0 dB (center, same for all three bands)
_LOW_FREQ_DEFAULT = 0.0881500244140625   # 90 Hz
_PEAK_FREQ_DEFAULT = 0.5057525634765625  # 1500 Hz
_HIGH_FREQ_DEFAULT = 0.8518218994140625  # 8000 Hz
_Q_DEFAULT = 0.26702880859375            # 0.27 (same for all three bands)

# One fully-described object per control:
#   'label'      : scribble-strip label (<= 7 chars)
#   'band'       : EQ band (0 = low shelf, 1 = peaking, 2 = high shelf)
#   'param'      : parameter type (Gain / Freq / Q)
#   'color'      : FL color int for the scribble strip (per shelf)
#   'ringMode'   : encoder ring display mode
#   'showCenter' : whether the ring's center LED is lit
#   'reversed'   : (Q only) ring fills wide->narrow as the value rises, since a high Q is a narrow band
#   'default'    : normalized fraction (0.0 - 1.0) an encoder click resets the control to
EQ_CONTROLS = [
    {'label': 'LowLvl',  'band': 0, 'param': Gain, 'color': _YELLOW, 'ringMode': mcu_knob_mode.BoostCut,  'showCenter': True,  'default': _GAIN_DEFAULT},
    {'label': 'LowFrq',  'band': 0, 'param': Freq, 'color': _YELLOW, 'ringMode': mcu_knob_mode.SingleDot, 'showCenter': False, 'default': _LOW_FREQ_DEFAULT},
    {'label': 'LowQ',    'band': 0, 'param': Q,    'color': _YELLOW, 'ringMode': mcu_knob_mode.Spread,    'showCenter': True,  'default': _Q_DEFAULT,  'reversed': True},
    {'label': 'PeakLvl', 'band': 1, 'param': Gain, 'color': _GREEN,  'ringMode': mcu_knob_mode.BoostCut,  'showCenter': True,  'default': _GAIN_DEFAULT},
    {'label': 'PeakFrq', 'band': 1, 'param': Freq, 'color': _GREEN,  'ringMode': mcu_knob_mode.SingleDot, 'showCenter': False, 'default': _PEAK_FREQ_DEFAULT},
    {'label': 'PeakQ',   'band': 1, 'param': Q,    'color': _GREEN,  'ringMode': mcu_knob_mode.Spread,    'showCenter': True,  'default': _Q_DEFAULT,  'reversed': True},
    {'label': 'HighLvl', 'band': 2, 'param': Gain, 'color': _CYAN,   'ringMode': mcu_knob_mode.BoostCut,  'showCenter': True,  'default': _GAIN_DEFAULT},
    {'label': 'HighFrq', 'band': 2, 'param': Freq, 'color': _CYAN,   'ringMode': mcu_knob_mode.SingleDot, 'showCenter': False, 'default': _HIGH_FREQ_DEFAULT},
    {'label': 'HighQ',   'band': 2, 'param': Q,    'color': _CYAN,   'ringMode': mcu_knob_mode.Spread,    'showCenter': True,  'default': _Q_DEFAULT,  'reversed': True},
]

# Number of EQ controls (3 bands x 3 parameters)
EqControlCount = len(EQ_CONTROLS)


def _clamp(value, low, high):
    return low if value < low else (high if value > high else value)


def control_of(virtualTrackIndex):
    """The full definition dict for a control index."""
    return EQ_CONTROLS[virtualTrackIndex]


def label_of(virtualTrackIndex):
    """The short scribble-strip label for a control index."""
    return EQ_CONTROLS[virtualTrackIndex]['label']


def color_of(virtualTrackIndex):
    """The FL Studio color int for a control index (per shelf)."""
    return EQ_CONTROLS[virtualTrackIndex]['color']


def ring_mode_of(virtualTrackIndex):
    """The encoder ring display mode for a control index."""
    return EQ_CONTROLS[virtualTrackIndex]['ringMode']


def reset_value_of(virtualTrackIndex):
    """
    The normalized event value (0..midi.FromMIDI_Max) an encoder click resets a control to,
    or None to fall back to center.
    """
    fraction = EQ_CONTROLS[virtualTrackIndex]['default']
    if fraction is None:
        return None
    return round(fraction * midi.FromMIDI_Max)  # type: ignore


def event_id_of(baseEventId, virtualIndex):
    """
    Returns the FL Studio event id for a control index, relative to the selected track's base plugin id
    (mixer.getTrackPluginId(track, 0)).
    """
    control = EQ_CONTROLS[virtualIndex]
    band = control['band']
    param = control['param']
    if param == Gain:
        return baseEventId + midi.REC_Mixer_EQ_Gain + band  # type: ignore
    if param == Freq:
        return baseEventId + midi.REC_Mixer_EQ_Freq + band  # type: ignore
    return baseEventId + midi.REC_Mixer_EQ_Q + band  # type: ignore


def ring_value_of(index, value):
    """
    Convert an FL Studio event value (0..midi.FromMIDI_Max) into a (showCenter, ledValue) pair for the
    encoder ring, based on the control's ring mode.
    """
    control = EQ_CONTROLS[index]
    showCenter = control['showCenter']
    fraction = value / midi.FromMIDI_Max  # type: ignore

    if control['ringMode'] == mcu_knob_mode.Spread:
        # Spread fills 1..6 outward from the center. Q is reversed: a high Q is a narrow, surgical band
        # so it should read narrow (few leds), while a low Q (wide band) reads wide.
        leds = round(fraction * 5)  # 0..5
        if control.get('reversed'):
            leds = 5 - leds
        return (showCenter, _clamp(1 + leds, 1, 6))

    # BoostCut (level, centered) / SingleDot (frequency) fill 1..11
    return (showCenter, _clamp(1 + round(fraction * 10), 1, 11))
