from constants import mcu_encoder

def CalculateEncoderMovementDelta(data2: int) -> int:
    """Convert MCU encoder data2 (signed magnitude, neutral=0x40) to a signed integer delta (negative = increase)."""
    if data2 >= mcu_encoder.EncoderMovementNeutral:
        return -(data2 - mcu_encoder.EncoderMovementNeutral)
    return data2

def CalculateMixerEncoderRes(steps: int) -> float:
    """Returns how much to change a mixer parameter per encoder turn, based on how fast the encoder is being turned."""
    return mcu_encoder.EncoderFineStep + ((abs(steps) - 1) / mcu_encoder.EncoderAccelerationScale)

def CalculateParamEncoderRes(steps: int) -> float:
    """Returns how much to change an FX plugin parameter per encoder turn, based on how fast the encoder is being turned. More fine-grained than mixer_encoder_res."""
    return mcu_encoder.ParamEncoderFineStep + ((abs(steps) - 1) / mcu_encoder.ParamEncoderAccelerationScale)
