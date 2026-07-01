# constants

FreeEventID = 400 # Base CC value for free events
FreeTrackCount = 64 # Number of tracks in free mode
EffectsSlotCount = 10 # Number of effect plugin slots per mixer track (banked through in Effects mode)
MidiCcBlockStart = 4096 # First index of the MIDI-CC block in a wrapped VST's 4240-param array; params from here up (128 MIDI-CC sends + 16 channel-aftertouch) are never real plugin parameters
ScribbleStripWidth = 7 # Width of the scribble strip in characters, used for truncating text to fit the screen
TrackCount = 8 # Number of tracks per hardware unit

ModeShortDescriptions = ('Pan', 'Stereo', 'Sends', 'EQ', 'Effects', 'Free')
ModeDescriptions = (
    'Panning                                (press to reset)',
    'Stereo separation                      (press to reset)',
    'Sends for selected track              (press to enable)',
    'EQ for selected track                  (press to reset)',
    'Effects for selected track            (press to enable)',
    'Lotsa free controls'
)
OffOnStr = ('off', 'on')
ArrowsStr = chr(0x3E) + chr(0x20) #ASCII for "> "
SyncLedVelocity = 0x7F
JogCC = 0x3C
