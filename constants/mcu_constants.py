# constants

FreeEventID = 400 # Base CC value for free events
FreeTrackCount = 64 # Number of tracks in free mode
ScribbleStripWidth = 7 # Width of the scribble strip in characters, used for truncating text to fit the screen

ModeShortDescriptions = ('Pan', 'Stereo', 'Sends', 'EQ', 'Effects', 'Free')
ModeDescriptions = (
    'Panning                                (press to reset)',
    'Stereo separation                      (press to reset)',
    'EQ for selected track                  (press to reset)',
    'Sends for selected track              (press to enable)',
    'Effects for selected track            (press to enable)',
    'Lotsa free controls'
)
OffOnStr = ('off', 'on')
ArrowsStr = chr(0x3E) + chr(0x20) #ASCII for "> "
SyncLedVelocity = 0x7F
