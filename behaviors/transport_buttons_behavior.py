import device
import midi
import transport

import constants.mcu_constants as mcu_constants
from behaviors.mcu_base_behavior import McuBaseBehavior
from device_hal import mcu_buttons
from device_hal.mcu_device import McuDevice
from utilities.button_manager import ButtonManager

class TransportButtonsBehavior(McuBaseBehavior):
    """Behavior to handle transport button presses (rewind/ff/stop/play/record)."""

    def __init__(self, mcuDevice: McuDevice):
        super().__init__(mcuDevice)

    def OnMidiMsg(self, event):
        # only handle note on/off events for transport buttons
        if event.midiId == midi.MIDI_NOTEON:
            
            # rewind / fast forward
            if event.data1 in [mcu_buttons.Rewind, mcu_buttons.FastForward]:
                if ButtonManager.ShiftPressed:
                    # when shift is held, use the transport buttons to adjust playback speed instead of normal transport behavior
                    if event.data2 == 0: # data 2 is 0 when the button is released, resets playback speed to 1
                        v2 = 1
                    elif event.data1 == mcu_buttons.Rewind:
                        v2 = 0.5 # rewind with shift is 0.5x playback speed
                    else:
                        v2 = 2 # fast forward with shift is 2x playback speed
                    transport.setPlaybackSpeed(v2)
                else:
                    # normal rewind/fast forward behavior
                    transport.globalTransport(midi.FPT_Rewind + int(event.data1 == mcu_buttons.FastForward), int(event.data2 > 0) * 2, event.pmeFlags)
                device.directFeedback(event)
                event.handled = True
                return event

            # stop/play/record
            elif event.data1 == mcu_buttons.Stop:
                transport.globalTransport(midi.FPT_Stop, int(event.data2 > 0) * 2, event.pmeFlags)
                event.handled = True
                return event

            elif event.data1 == mcu_buttons.Play:
                transport.globalTransport(midi.FPT_Play, int(event.data2 > 0) * 2, event.pmeFlags)
                event.handled = True
                return event

            elif event.data1 == mcu_buttons.Record:
                transport.globalTransport(midi.FPT_Record, int(event.data2 > 0) * 2, event.pmeFlags)
                event.handled = True
                return event

        return super().OnMidiMsg(event)

    def OnRefresh(self, flags):
        # Update stop/record LEDs when requested
        if flags & midi.HW_Dirty_LEDs:
            isRecording = transport.isRecording()
            # Record LED
            self.McuDevice.SetButton(mcu_buttons.Record, midi.TranzPort_OffOnT[isRecording], 2, skipIsAssignedCheck=True)
            # Stop LED: on when playback stopped
            self.McuDevice.SetButton(mcu_buttons.Stop, midi.TranzPort_OffOnT[transport.isPlaying() == midi.PM_Stopped], 0, skipIsAssignedCheck=True)
        super().OnRefresh(flags)

    def OnUpdateBeatIndicator(self, Value: int):
        super().OnUpdateBeatIndicator(Value)

        # Flash the Play button as the beat indicator updates.
        if device.isAssigned():
            # Depending on the value, a different message is sent to the play button
            syncLEDMsg = [
                midi.MIDI_NOTEON,
                midi.MIDI_NOTEON + (mcu_constants.SyncLedVelocity << 16),
                midi.MIDI_NOTEON + (mcu_constants.SyncLedVelocity << 16)
            ]
            self.McuDevice.SetButton(mcu_buttons.Play, syncLEDMsg[Value], 128)
