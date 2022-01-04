# name=FLtouch X-Touch Extender
# url=https://github.com/bramdebouvere/fltouch
# receiveFrom=FLtouch X-Touch
# supportedDevices=X-Touch-Ext

import patterns
import mixer
import device
import transport
import arrangement
import general
import launchMapPages
import playlist
import ui
import channels

import midi
import utils
import time

import debug
import mcu_pages
import mcu_buttons

MackieCU_KnobOffOnT = [(midi.MIDI_CONTROLCHANGE + (1 << 6)) << 16, midi.MIDI_CONTROLCHANGE + ((0xB + (2 << 4) + (1 << 6)) << 16)]
MackieCU_nFreeTracks = 64

class TMackieCol:
	def __init__(self):
		self.TrackNum = 0
		self.BaseEventID = 0
		self.KnobEventID = 0 
		self.KnobPressEventID = 0
		self.KnobResetEventID = 0
		self.KnobResetValue = 0
		self.KnobMode = 0
		self.KnobCenter = 0
		self.SliderEventID = 0
		self.Peak = 0
		self.Tag = 0
		self.SliderName = ""
		self.KnobName = ""
		self.LastValueIndex = 0
		self.ZPeak = False
		self.Dirty = False
		self.KnobHeld = False

class TMackieCU_Ext():
	def __init__(self):
		self.LastMsgLen = 0x37
		self.MsgT = ["", ""]

		self.Shift = False
		self.MsgDirty = False
		self.SliderHoldCount = 0
		self.FirstTrack = 0
		self.FirstTrackT = [0, 0]
		self.ColT = [0 for x in range(9)]
		for x in range(0, 9):
			self.ColT[x] = TMackieCol()

		self.FreeCtrlT = [0 for x in range(MackieCU_nFreeTracks - 1 + 2)]  # 64+1 sliders
		self.Clicking = False
		self.SmoothSpeed = 0
		self.MeterMax = 0
		self.ActivityMax = 0
		self.MackieCU_PageNameT = ('Panning                                (press to reset)', 'Stereo separation                      (press to reset)',  'Sends for selected track              (press to enable)', 'Effects for selected track            (press to enable)', 'EQ for selected track                  (press to reset)',  'Lotsa free controls')
		self.AlphaTrack_SliderMax = round(13072 * 16000 / 12800)
		self.Flip = False
		self.FreeEventID = 400
		self.Page = 0

	def OnInit(self):

		self.FirstTrackT[0] = 1
		self.FirstTrack = 0
		self.SmoothSpeed = 0
		self.Clicking = True

		device.setHasMeters()
		for m in range(0, len(self.FreeCtrlT)):
			self.FreeCtrlT[m] = 8192 # default free faders to center
		if device.isAssigned():
			device.midiOutSysex(bytes([0xF0, 0x00, 0x00, 0x66, 0x15, 0x0C, 1, 0xF7]))

		self.SetBackLight(2) # backlight timeout to 2 minutes
		self.UpdateClicking()
		self.UpdateMeterMode()

		self.SetPage(self.Page)
		self.OnSendMsg('Linked to ' + ui.getProgTitle() + ' (' + ui.getVersion() + ')')
		print('OnInit ready')

	def OnDeInit(self):

		if device.isAssigned():

			for m in range(0, 8):
				device.midiOutSysex(bytes([0xF0, 0x00, 0x00, 0x66, 0x15, 0x20, m, 0, 0xF7]))

			if ui.isClosing():
				self.SendMsg(ui.getProgTitle() + ' session closed at ' + time.ctime(time.time()), 0)
			else:
				self.SendMsg('')

			self.SendMsg('', 1)
			self.SendAssignmentMsg('  ')

		print('OnDeInit ready')

	def OnDirtyMixerTrack(self, SetTrackNum):

		for m in range(0, len(self.ColT)):
			if (self.ColT[m].TrackNum == SetTrackNum) | (SetTrackNum == -1):
				self.ColT[m].Dirty = True

	def OnRefresh(self, flags):

		if flags & midi.HW_Dirty_Mixer_Sel:
			self.UpdateMixer_Sel()

		if flags & midi.HW_Dirty_Mixer_Display:
			self.UpdateTextDisplay()
			self.UpdateColT()

		if flags & midi.HW_Dirty_Mixer_Controls:
			for n in range(0, len(self.ColT)):
				if self.ColT[n].Dirty:
					self.UpdateCol(n)

		# LEDs
		if flags & midi.HW_Dirty_LEDs:
			self.UpdateLEDs()

	def OnMidiMsg(self, event):
		if (event.midiId == midi.MIDI_CONTROLCHANGE):
			if (event.midiChan == 0):
				event.inEv = event.data2
				if event.inEv >= 0x40:
					event.outEv = -(event.inEv - 0x40)
				else:
					event.outEv = event.inEv

				# knobs
				if event.data1 in [0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17]:
					Res = 0.005 + ((abs(event.outEv)-1) / 2000)
					if self.Page == mcu_pages.Free:
						i = event.data1 - 0x10
						self.ColT[i].Peak = self.ActivityMax
						event.data1 = self.ColT[i].BaseEventID + int(self.ColT[i].KnobHeld)
						event.isIncrement = 1
						s = chr(0x2B + int(event.outEv < 0)*2) # + or - sign depending on how you rotate
						self.OnSendMsg('Free knob ' + str(event.data1) + ': ' + s + str(abs(event.outEv)))
						device.processMIDICC(event)
						device.hardwareRefreshMixerTrack(self.ColT[i].TrackNum)
					else:
						self.SetKnobValue(event.data1 - 0x10, event.outEv, Res)
						event.handled = True
				else:
					event.handled = False # for extra CCs in emulators
			else:
				event.handled = False # for extra CCs in emulators

		elif event.midiId == midi.MIDI_PITCHBEND: # pitch bend (faders)

			if event.midiChan <= 8:
				event.inEv = event.data1 + (event.data2 << 7)
				event.outEv = (event.inEv << 16) // 16383
				event.inEv -= 0x2000

				if self.Page == mcu_pages.Free:
					self.ColT[event.midiChan].Peak = self.ActivityMax
					self.FreeCtrlT[self.ColT[event.midiChan].TrackNum] = event.data1 + (event.data2 << 7)
					device.hardwareRefreshMixerTrack(self.ColT[event.midiChan].TrackNum)
					event.data1 = self.ColT[event.midiChan].BaseEventID + 7
					event.midiChan = 0
					event.midiChanEx = 0
					self.OnSendMsg('Free slider ' + str(event.data1) + ': ' + ui.getHintValue(event.outEv, 65523))
					event.status = event.midiId = midi.MIDI_CONTROLCHANGE
					event.isIncrement = 0
					event.outEv = int(event.data2 / 127.0 * midi.FromMIDI_Max)
					device.processMIDICC(event)
				elif self.ColT[event.midiChan].SliderEventID >= 0:
					# slider (mixer track volume)
					event.handled = True
					mixer.automateEvent(self.ColT[event.midiChan].SliderEventID, self.AlphaTrack_SliderToLevel(event.inEv + 0x2000), midi.REC_MIDIController, self.SmoothSpeed)
					# hint
					n = mixer.getAutoSmoothEventValue(self.ColT[event.midiChan].SliderEventID)
					s = mixer.getEventIDValueString(self.ColT[event.midiChan].SliderEventID, n)
					if s != '':
						s = ': ' + s
					self.OnSendMsg(self.ColT[event.midiChan].SliderName + s)

		elif (event.midiId == midi.MIDI_NOTEON) | (event.midiId == midi.MIDI_NOTEOFF):  # NOTE
			if event.midiId == midi.MIDI_NOTEON:
				if (event.pmeFlags & midi.PME_FromScript != 0):
					if event.data1 == 0x7F:
						self.SetFirstTrack(event.data2)
				# slider hold
				if (event.data1 in [104, 105, 106, 107, 108, 109, 110, 111, 112]):
					self.SliderHoldCount += -1 + (int(event.data2 > 0) * 2)
					# Auto select channel
					if event.data1 != 112 and event.data2 > 0 and (self.Page == mcu_pages.Pan or self.Page == mcu_pages.Stereo):
						fader_index = event.data1 - 104
						if mixer.trackNumber != self.ColT[fader_index].TrackNum:
							mixer.setTrackNumber(self.ColT[fader_index].TrackNum)
					event.handled = True
					return

				if (event.pmeFlags & midi.PME_System != 0):
					if event.data1 == 0x34: # display mode
						if event.data2 > 0:
							pass #don't react, this button (name/value) can do other stuff now
							#self.MeterMode = (self.MeterMode + 1) % 3
							#self.OnSendMsg(self.MackieCU_MeterModeNameT[self.MeterMode])
							#self.UpdateMeterMode()
					elif (event.data1 == 0x2E) | (event.data1 == 0x2F): # mixer bank
						if event.data2 > 0:
							self.SetFirstTrack(self.FirstTrackT[self.FirstTrack] - 8 + int(event.data1 == 0x2F) * 16)
					elif (event.data1 == 0x30) | (event.data1 == 0x31):
						if event.data2 > 0:
							self.SetFirstTrack(self.FirstTrackT[self.FirstTrack] - 1 + int(event.data1 == 0x31) * 2)
					elif event.data1 == 0x32: # self.Flip
						if event.data2 > 0:
							self.Flip = not self.Flip
							self.UpdateColT()
							self.UpdateLEDs()
					elif event.data1 in [0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27]: # knob reset
						if self.Page == mcu_pages.Free:
							i = event.data1 - 0x20
							self.ColT[i].KnobHeld = event.data2 > 0
							if event.data2 > 0:
								self.ColT[i].Peak = self.ActivityMax
								event.data1 = self.ColT[i].BaseEventID + 2
								event.outEv = 0
								event.isIncrement = 2
								self.OnSendMsg('Free knob switch ' + str(event.data1))
								device.processMIDICC(event)
							device.hardwareRefreshMixerTrack(self.ColT[i].TrackNum)
							return
						elif event.data2 > 0:
							n = event.data1 - 0x20
							if self.Page == mcu_pages.Sends:
								if mixer.setRouteTo(mixer.trackNumber(), self.ColT[n].TrackNum, -1) < 0:
									self.OnSendMsg('Cannot send to this track')
								else:
									mixer.afterRoutingChanged()
							else:
								self.SetKnobValue(n, midi.MaxInt)

					elif (event.data1 >= 0) & (event.data1 <= 0x1F): # free hold buttons
						if self.Page == mcu_pages.Free:
							i = event.data1 % 8
							self.ColT[i].Peak = self.ActivityMax
							event.data1 = self.ColT[i].BaseEventID + 3 + event.data1 // 8
							event.inEv = event.data2
							event.outEv = int(event.inEv > 0) * midi.FromMIDI_Max
							self.OnSendMsg('Free button ' + str(event.data1) + ': ' + OffOnStr[event.outEv > 0])
							device.processMIDICC(event)
							device.hardwareRefreshMixerTrack(self.ColT[i].TrackNum)
							return

					elif event.data1 in [mcu_buttons.Pan, mcu_buttons.Sends, mcu_buttons.Equalizer, mcu_buttons.Stereo, mcu_buttons.Effects, mcu_buttons.Free]: # self.Page
						#self.SliderHoldCount +=  -1 + (int(event.data2 > 0) * 2)
						if event.data2 > 0:
							n = event.data1 - mcu_buttons.Pan
							self.OnSendMsg(self.MackieCU_PageNameT[n])
							self.SetPage(n)
							#device.dispatch(0, midi.MIDI_NOTEON + (event.data1 << 8) + (event.data2 << 16) )

				if (event.pmeFlags & midi.PME_System_Safe != 0):
					if event.data1 == 0x47: # link selected channels to current mixer track
						if event.data2 > 0:
							if self.Shift:
								mixer.linkTrackToChannel(midi.ROUTE_StartingFromThis)
							else:
								mixer.linkTrackToChannel(midi.ROUTE_ToThis)
					elif (event.data1 >= 0x18) & (event.data1 <= 0x1F): # select mixer track
						if event.data2 > 0:
							i = event.data1 - 0x18
							ui.showWindow(midi.widMixer)
							mixer.setTrackNumber(self.ColT[i].TrackNum, midi.curfxScrollToMakeVisible | midi.curfxMinimalLatencyUpdate)

					elif (event.data1 >= 0x8) & (event.data1 <= 0xF): # solo
						if event.data2 > 0:
							i = event.data1 - 0x8
							self.ColT[i].solomode = midi.fxSoloModeWithDestTracks
							if self.Shift:
								Include(self.ColT[i].solomode, midi.fxSoloModeWithSourceTracks)
							mixer.soloTrack(self.ColT[i].TrackNum, midi.fxSoloToggle, self.ColT[i].solomode)
							mixer.setTrackNumber(self.ColT[i].TrackNum, midi.curfxScrollToMakeVisible)

					elif (event.data1 >= 0x10) & (event.data1 <= 0x17): # mute
						if event.data2 > 0:
							mixer.enableTrack(self.ColT[event.data1 - 0x10].TrackNum)

					elif (event.data1 >= 0x0) & (event.data1 <= 0x7): # arm
						if event.data2 > 0:
							mixer.armTrack(self.ColT[event.data1].TrackNum)
							if mixer.isTrackArmed(self.ColT[event.data1].TrackNum):
								self.OnSendMsg(mixer.getTrackName(self.ColT[event.data1].TrackNum) + ' recording to ' + mixer.getTrackRecordingFileName(self.ColT[event.data1].TrackNum))
							else:
								self.OnSendMsg(mixer.getTrackName(self.ColT[event.data1].TrackNum) + ' unarmed')

					event.handled = True
				else:
					event.handled = False
			else:
				event.handled = False

	def SendMsg(self, Msg, Row = 0):

		sysex = bytearray([0xF0, 0x00, 0x00, 0x66, 0x15, 0x12, (self.LastMsgLen + 1) * Row]) + bytearray(Msg.ljust(self.LastMsgLen + 1, ' ')[:56], 'utf-8')
		sysex.append(0xF7)
		device.midiOutSysex(bytes(sysex))

	def SendAssignmentMsg(self, Msg):
		s_ansi = Msg[-2:]
		if device.isAssigned():
			for m in range(1, 3):
				device.midiOutMsg(midi.MIDI_CONTROLCHANGE + ((0x4C - m) << 8) + (ord(s_ansi[m-1]) << 16))

	def UpdateMsg(self):
		self.SendMsg(self.MsgT[1])

	def OnSendMsg(self, Msg):
		self.MsgT[1] = Msg
		self.MsgDirty = True

	def UpdateTextDisplay(self):

		s1 = ''
		for m in range(0, len(self.ColT) - 1):
			s = ''
			if self.Page == mcu_pages.Free:
				s = '  ' + utils.Zeros(self.ColT[m].TrackNum + 1, 2, ' ')
			else:
				s = mixer.getTrackName(self.ColT[m].TrackNum, 7)
			for n in range(1, 7 - len(s) + 1):
				s = s + ' '
			s1 = s1 + s

		self.SendMsg(s1, 1)

	def GetSplitMarks(self):
		s2 = ''
		for m in range(0, len(self.ColT) - 1):
			s2 = s2 + '      .'
		return s2

	def UpdateMeterMode(self):
		if device.isAssigned():
			#clear peak indicators
			for m in range(0, len(self.ColT) - 1):
				device.midiOutMsg(midi.MIDI_CHANAFTERTOUCH + (0xF << 8) + (m << 12))
			# disable all meters
			for m in range(0, 8):
				device.midiOutSysex(bytes([0xF0, 0x00, 0x00, 0x66, 0x15, 0x20, m, 0, 0xF7]))

		# reset stuff
		self.MeterMax = 0xD + 1 # $D for horizontal, $E for vertical meters
		self.ActivityMax = 0xD - 1 * 6

		self.UpdateTextDisplay()

		if device.isAssigned():
			# vertical meter mode
			device.midiOutSysex(bytes([0xF0, 0x00, 0x00, 0x66, 0x15, 0x21, 1, 0xF7]))

			# enable all meters
			for m  in range(0, 8):
				device.midiOutSysex(bytes([0xF0, 0x00, 0x00, 0x66, 0x15, 0x20, m, 3, 0xF7]))

	def SetPage(self, Value):

		oldPage = self.Page
		self.Page = Value

		self.FirstTrack = int(self.Page == mcu_pages.Free)
		#if self.Page == oldPage:
		self.SetFirstTrack(self.FirstTrackT[self.FirstTrack])

		if self.Page == mcu_pages.Free:

			BaseID = midi.EncodeRemoteControlID(device.getPortNumber(), 0, self.FreeEventID + 7)
			for n in range(0, len(self.FreeCtrlT)):
				d = mixer.remoteFindEventValue(BaseID + n * 8, 1)
				if d >= 0:
					self.FreeCtrlT[n] = min(round(d * 16384), 16384)

		if (oldPage == mcu_pages.Free) | (self.Page == mcu_pages.Free):
			self.UpdateMeterMode()
		self.UpdateColT()
		self.UpdateLEDs()
		self.UpdateTextDisplay()

	def UpdateMixer_Sel(self):

		if device.isAssigned():
			for m in range(0, len(self.ColT) - 1):
				device.midiOutNewMsg(((0x18 + m) << 8) + midi.TranzPort_OffOnT[self.ColT[m].TrackNum == mixer.trackNumber()], self.ColT[m].LastValueIndex + 4)

	def UpdateCol(self, Num):

		data1 = 0
		data2 = 0
		baseID = 0
		center = 0
		b = False

		if device.isAssigned():
			if self.Page == mcu_pages.Free:
				baseID = midi.EncodeRemoteControlID(device.getPortNumber(), 0, self.ColT[Num].BaseEventID)
				# slider
				m = self.FreeCtrlT[self.ColT[Num].TrackNum]
				device.midiOutNewMsg(midi.MIDI_PITCHBEND + Num + ((m & 0x7F) << 8) + ((m >> 7) << 16), self.ColT[Num].LastValueIndex + 5)
				if Num < 8:
					# ring
					d = mixer.remoteFindEventValue(baseID + int(self.ColT[Num].KnobHeld))
					if d >= 0:
						m = 1 + round(d * 10)
					else:
						m = int(self.ColT[Num].KnobHeld) * (11 + (2 << 4))
					device.midiOutNewMsg(midi.MIDI_CONTROLCHANGE + ((0x30 + Num) << 8) + (m << 16), self.ColT[Num].LastValueIndex)
					# buttons
					for n in range(0, 4):
						d = mixer.remoteFindEventValue(baseID + 3 + n)
						if d >= 0:
							b = d >= 0.5
						else:
							b = False

						device.midiOutNewMsg(((n * 8 + Num) << 8) + midi.TranzPort_OffOnT[b], self.ColT[Num].LastValueIndex + 1 + n)
			else:
				sv = mixer.getEventValue(self.ColT[Num].SliderEventID)

				if Num < 8:
					# V-Pot
					center = self.ColT[Num].KnobCenter
					if self.ColT[Num].KnobEventID >= 0:
						m = mixer.getEventValue(self.ColT[Num].KnobEventID, midi.MaxInt, False)
						if center < 0:
							if self.ColT[Num].KnobResetEventID == self.ColT[Num].KnobEventID:
								center = int(m !=  self.ColT[Num].KnobResetValue)
							else:
								center = int(sv !=  self.ColT[Num].KnobResetValue)

						if self.ColT[Num].KnobMode < 2:
							data1 = 1 + round(m * (10 / midi.FromMIDI_Max))
						else:
							data1 = round(m * (11 / midi.FromMIDI_Max))
						if self.ColT[Num].KnobMode > 3:
							data1 = (center << 6)
						else:
							data1 = data1 + (self.ColT[Num].KnobMode << 4) + (center << 6)
					else:
						data1 = 0

					device.midiOutNewMsg(midi.MIDI_CONTROLCHANGE + ((0x30 + Num) << 8) + (data1 << 16), self.ColT[Num].LastValueIndex)

					# arm, solo, mute
					device.midiOutNewMsg( ((0x00 + Num) << 8) + midi.TranzPort_OffOnBlinkT[int(mixer.isTrackArmed(self.ColT[Num].TrackNum)) * (1 + int(transport.isRecording()))], self.ColT[Num].LastValueIndex + 1)
					device.midiOutNewMsg( ((0x08 + Num) << 8) + midi.TranzPort_OffOnT[mixer.isTrackSolo(self.ColT[Num].TrackNum)], self.ColT[Num].LastValueIndex + 2)
					device.midiOutNewMsg( ((0x10 + Num) << 8) + midi.TranzPort_OffOnT[not mixer.isTrackEnabled(self.ColT[Num].TrackNum)], self.ColT[Num].LastValueIndex + 3)

				# slider
				data1 = self.AlphaTrack_LevelToSlider(sv)
				data2 = data1 & 127
				data1 = data1 >> 7
				device.midiOutNewMsg(midi.MIDI_PITCHBEND + Num + (data2 << 8) + (data1 << 16), self.ColT[Num].LastValueIndex + 5)

			self.ColT[Num].Dirty = False

	def AlphaTrack_LevelToSlider(self, Value, Max = midi.FromMIDI_Max):

		return round(Value / Max * self.AlphaTrack_SliderMax)

	def AlphaTrack_SliderToLevel(self, Value, Max = midi.FromMIDI_Max):

		return min(round(Value / self.AlphaTrack_SliderMax * Max), Max)

	def UpdateColT(self):
		f = self.FirstTrackT[self.FirstTrack]
		CurID = mixer.getTrackPluginId(mixer.trackNumber(), 0)

		for m in range(0, len(self.ColT)):
			if self.Page == mcu_pages.Free:
				# free controls
				if m == 8:
					self.ColT[m].TrackNum = MackieCU_nFreeTracks
				else:
					self.ColT[m].TrackNum = (f + m) % MackieCU_nFreeTracks

				self.ColT[m].KnobName = 'Knob ' + str(self.ColT[m].TrackNum + 1)
				self.ColT[m].SliderName = 'Slider ' + str(self.ColT[m].TrackNum + 1)

				self.ColT[m].BaseEventID = self.FreeEventID + self.ColT[m].TrackNum * 8 # first virtual CC
			else:
				self.ColT[m].KnobPressEventID = -1

				# mixer
				if m == 8:
					self.ColT[m].TrackNum = -2
					self.ColT[m].BaseEventID = midi.REC_MainVol
					self.ColT[m].SliderEventID = self.ColT[m].BaseEventID
					self.ColT[m].SliderName = 'Master Vol'
				else:
					self.ColT[m].TrackNum = midi.TrackNum_Master + ((f + m) % mixer.trackCount())
					self.ColT[m].BaseEventID = mixer.getTrackPluginId(self.ColT[m].TrackNum, 0)
					self.ColT[m].SliderEventID = self.ColT[m].BaseEventID + midi.REC_Mixer_Vol
					s = mixer.getTrackName(self.ColT[m].TrackNum)
					self.ColT[m].SliderName = s + ' - Vol'

					self.ColT[m].KnobEventID = -1
					self.ColT[m].KnobResetEventID = -1
					self.ColT[m].KnobResetValue = midi.FromMIDI_Max >> 1
					self.ColT[m].KnobName = ''
					self.ColT[m].KnobMode = 1 # parameter, pan, volume, off
					self.ColT[m].KnobCenter = -1

					if self.Page == mcu_pages.Pan:
						self.ColT[m].KnobEventID = self.ColT[m].BaseEventID + midi.REC_Mixer_Pan
						self.ColT[m].KnobResetEventID = self.ColT[m].KnobEventID
						self.ColT[m].KnobName = mixer.getTrackName( self.ColT[m].TrackNum) + ' - ' + 'Pan'
					elif self.Page == mcu_pages.Stereo:
						self.ColT[m].KnobEventID = self.ColT[m].BaseEventID + midi.REC_Mixer_SS
						self.ColT[m].KnobResetEventID = self.ColT[m].KnobEventID
						self.ColT[m].KnobName = mixer.getTrackName(self.ColT[m].TrackNum) + ' - ' + 'Sep'
					elif self.Page == mcu_pages.Sends:
						self.ColT[m].KnobEventID = CurID + midi.REC_Mixer_Send_First + self.ColT[m].TrackNum
						s = mixer.getEventIDName(self.ColT[m].KnobEventID)
						self.ColT[m].KnobName = s
						self.ColT[m].KnobResetValue = round(12800 * midi.FromMIDI_Max / 16000)
						self.ColT[m].KnobCenter = mixer.getRouteSendActive(mixer.trackNumber(),self.ColT[m].TrackNum)
						if self.ColT[m].KnobCenter == 0:
							self.ColT[m].KnobMode = 4
						else:
							self.ColT[m].KnobMode = 2
					elif self.Page == mcu_pages.Effects:
						CurID = mixer.getTrackPluginId(mixer.trackNumber(), m)

						self.ColT[m].KnobEventID = CurID + midi.REC_Plug_MixLevel
						s = mixer.getEventIDName(self.ColT[m].KnobEventID)
						self.ColT[m].KnobName = s
						self.ColT[m].KnobResetValue = midi.FromMIDI_Max

						IsValid = mixer.isTrackPluginValid(mixer.trackNumber(), m)
						IsEnabledAuto = mixer.isTrackAutomationEnabled(mixer.trackNumber(), m)
						if IsValid:
							self.ColT[m].KnobMode = 2
							self.ColT[m].KnobPressEventID = CurID + midi.REC_Plug_Mute
						else:
							self.ColT[m].KnobMode = 4
						self.ColT[m].KnobCenter = int(IsValid & IsEnabledAuto)
					elif self.Page == mcu_pages.Equalizer:
						# turn off knobs and sliders in EQ on extender
						self.ColT[m].SliderEventID = -1
						self.ColT[m].KnobEventID = -1
						self.ColT[m].KnobMode = 4

					# self.Flip knob & slider
					if self.Flip:
						self.ColT[m].KnobEventID, self.ColT[m].SliderEventID = utils.SwapInt(self.ColT[m].KnobEventID, self.ColT[m].SliderEventID)
						s = self.ColT[m].SliderName
						self.ColT[m].SliderName = self.ColT[m].KnobName
						self.ColT[m].KnobName = s
						self.ColT[m].KnobMode = 2
						if not (self.Page in [mcu_pages.Sends, mcu_pages.Effects]): # , MackieCUPage_EQ
							self.ColT[m].KnobCenter = -1
							self.ColT[m].KnobResetValue = round(12800 * midi.FromMIDI_Max / 16000)
							self.ColT[m].KnobResetEventID = self.ColT[m].KnobEventID

			self.ColT[m].LastValueIndex = 48 + m * 6
			self.ColT[m].Peak = 0
			self.ColT[m].ZPeak = False
			self.UpdateCol(m)

	def SetKnobValue(self, Num, Value, Res = midi.EKRes):
		if (self.ColT[Num].KnobEventID >= 0) & (self.ColT[Num].KnobMode < 4):
			if Value == midi.MaxInt:
				if self.Page == mcu_pages.Effects:
					if self.ColT[Num].KnobPressEventID >= 0:

						Value = channels.incEventValue(self.ColT[Num].KnobPressEventID, 0, midi.EKRes)
						channels.processRECEvent(self.ColT[Num].KnobPressEventID, Value, midi.REC_Controller)
						s = mixer.getEventIDName(self.ColT[Num].KnobPressEventID)
						self.OnSendMsg(s)
					return
				else:
					mixer.automateEvent(self.ColT[Num].KnobResetEventID, self.ColT[Num].KnobResetValue, midi.REC_MIDIController, self.SmoothSpeed)
			else:
				mixer.automateEvent(self.ColT[Num].KnobEventID, Value, midi.REC_Controller, self.SmoothSpeed, 1, Res)

			# hint
			n = mixer.getAutoSmoothEventValue(self.ColT[Num].KnobEventID)
			s = mixer.getEventIDValueString(self.ColT[Num].KnobEventID, n)
			if s !=  '':
				s = ': ' + s
			self.OnSendMsg(self.ColT[Num].KnobName + s)

	def SetFirstTrack(self, Value):

		self.FirstTrackT[self.FirstTrack] = (Value + mixer.trackCount()) % mixer.trackCount()
		s = utils.Zeros(self.FirstTrackT[self.FirstTrack], 2, ' ')
		self.UpdateColT()
		self.SendAssignmentMsg(s)
		device.hardwareRefreshMixerTrack(-1)

	def OnUpdateMeters(self):
		if self.Page != mcu_pages.Free:
			for m in range(0, len(self.ColT) - 1):
				currentPeak = mixer.getTrackPeaks(self.ColT[m].TrackNum, midi.PEAK_LR_INV)
				meterValue = int(currentPeak * self.MeterMax)
				if (currentPeak > 0.001 and meterValue == 0):
					meterValue = 1 #if there is any activity, make sure the lowest led burns
				self.ColT[m].Peak = max(self.ColT[m].Peak, meterValue)

	def OnIdle(self):

		# refresh meters
		if device.isAssigned():
			f = False
			for m in range(0, len(self.ColT) - 1):
				self.ColT[m].Tag = utils.Limited(self.ColT[m].Peak, 0, self.MeterMax)
				self.ColT[m].Peak = 0
				if self.ColT[m].Tag == 0:
					if self.ColT[m].ZPeak:
						continue
					else:
						self.ColT[m].ZPeak = True
				else:
					self.ColT[m].ZPeak = f
				device.midiOutMsg(midi.MIDI_CHANAFTERTOUCH + (self.ColT[m].Tag << 8) + (m << 12))

		# temp message
		if self.MsgDirty:
			self.UpdateMsg()
			self.MsgDirty = False
	def UpdateLEDs(self):

		if device.isAssigned():
			r = transport.isRecording()
			b = 0
			for m in range(0, mixer.trackCount()):
				if mixer.isTrackArmed(m):
					b = 1 + int(r)
					break

			device.midiOutNewMsg((0x73 << 8) + midi.TranzPort_OffOnBlinkT[b], 16)

	def UpdateClicking(self): # switch self.Clicking for transport buttons

		if device.isAssigned():
			device.midiOutSysex(bytes([0xF0, 0x00, 0x00, 0x66, 0x15, 0x0A, int(self.Clicking), 0xF7]))

	def SetBackLight(self, Minutes): # set backlight timeout (0 should switch off immediately, but doesn't really work well)

		if device.isAssigned():
			device.midiOutSysex(bytes([0xF0, 0x00, 0x00, 0x66, 0x15, 0x0B, Minutes, 0xF7]))

MackieCU_Ext = TMackieCU_Ext()

def OnInit():
	MackieCU_Ext.OnInit()

def OnDeInit():
	MackieCU_Ext.OnDeInit()

def OnDirtyMixerTrack(SetTrackNum):
	MackieCU_Ext.OnDirtyMixerTrack(SetTrackNum)

def OnRefresh(Flags):
	MackieCU_Ext.OnRefresh(Flags)

def OnMidiMsg(event):
	MackieCU_Ext.OnMidiMsg(event)

def OnSendTempMsg(Msg, Duration = 1000):
	MackieCU_Ext.OnSendMsg(Msg)

def OnUpdateMeters():
	MackieCU_Ext.OnUpdateMeters()

def OnIdle():
	MackieCU_Ext.OnIdle()

