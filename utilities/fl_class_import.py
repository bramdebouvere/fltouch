# Utilities class for importing types from fl_classes
# While the types exist at runtime, "fl_classes" is not something that can be imported at runtime
# For more info see https://il-group.github.io/FL-Studio-API-Stubs/midi_controller_scripting/fl_classes/

try:
    from fl_classes import FlMidiMsg
except ImportError:
    FlMidiMsg = 'FlMidiMsg'
