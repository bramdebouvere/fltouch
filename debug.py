# Contains functions that come in handy when debugging

def PrintMidiInfo(event):  # quick code to see info about particular midi control (check format function in python)
	print("EVENT (handled: {}, timestamp: {}, status: {}, data1: {}, data2: {}, port: {}, sysex: {}, midiId: {}, midiChan: {}, midiChanEx: {}, isIncrement: {}, inEv: {}, outEv: {}, controlNum: {}, controlVal: {}, res: {}, note:{})".format(event.handled, event.timestamp, event.status, event.data1, event.data2, event.port, HexIt(event.sysex), event.midiId, event.midiChan, event.midiChanEx, event.isIncrement, event.inEv, event.outEv, event.controlNum, event.controlVal, event.res, event.note))

def HexIt(sysex):  # turns whatever is given to hexadecimal number, if it's not something you can turn, returns none
		if sysex:
			return sysex.hex()
		else:
			return "None"