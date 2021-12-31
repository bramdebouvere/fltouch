# Contains functions that come in handy when debugging

def PrintMidiInfo(Event):  # quick code to see info about particular midi control (check format function in python)
	print("EVENT (handled: {}, timestamp: {}, status: {}, data1: {}, data2: {}, port: {}, sysex: {}, midiId: {}, midiChan: {}, midiChanEx: {}, isIncrement: {}, inEv: {}, outEv: {}, controlNum: {}, controlVal: {}, res: {}, note:{})".format(Event.handled, Event.timestamp, Event.status, Event.data1, Event.data2, Event.port, HexIt(Event.sysex), Event.midiId, Event.midiChan, Event.midiChanEx, Event.isIncrement, Event.inEv, Event.outEv, Event.controlNum, Event.controlVal, Event.res, Event.note))

def HexIt(SysEx):  # turns whatever is given to hexadecimal number, if it's not something you can turn, returns none
		if SysEx:
			return SysEx.hex()
		else:
			return "None"