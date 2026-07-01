# MCU encoder specific CC protocol values and tuning constants.

# Encoder CCs
EncoderCcBase = 0x10 # first encoder
EncoderCcLast = 0x17 # last encoder

# data2 neutral cc value: below = left rotation, above = right rotation
EncoderMovementNeutral = 0x40

# Encoder step sizing.
# Tune these to change the feel of all mixer-parameter encoders (pan, stereo, sends, EQ, FX slot level).
EncoderFineStep = 0.005
EncoderAccelerationScale = 2000 # acceleration on faster turns (smaller = ramps up faster)

# Plugin parameter encoder step sizing (is a bit more finegrained).
# setParamValue takes a normalized 0.0-1.0 float, so these are independent of the MIDI range.
ParamEncoderFineStep = 0.002       # step per detent when turning slowly (lower = finer)
ParamEncoderAccelerationScale = 800     # acceleration on faster turns (smaller = ramps up faster)

# LED ring range: 0 = all LEDs off, 1-LedWrapMax = fill up to that position
LedWrapMax = 11
