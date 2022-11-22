# Contains functions that come in handy when debugging

def print_midi_info(event):
    "Quick code to see info about particular midi control (uses f-strings for formating)"
    print(
        f"EVENT (handled: {event.handled}, timestamp: {event.timestamp}"
        f", status: {event.status}, data1: {event.data1}, data2: {event.data2}"
        f", port: {event.port}, sysex: {hex_it(event.sysex)}, midiId: {event.midiId}"
        f", midiChan: {event.midiChan}, midiChanEx: {event.midiChanEx}"
        f", isIncrement: {event.isIncrement}, inEv: {event.inEv}, outEv: {event.outEv}"
        f", controlNum: {event.controlNum}, controlVal: {event.controlVal}"
        f", res: {event.res}, note:{event.note})")


def hex_it(sysex: bytes):
    """Returns whatever is given as a string formatted hexadecimal number

    If there is no data to convert, returns reason as a string"""
    if not sysex:
        return 'Not set'
    elif len(sysex) == 0:
        return 'No data'
    else:
        return str(sysex)
