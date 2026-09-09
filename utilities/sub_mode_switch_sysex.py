# Encode/decode functions for McuCompositeMode's sub-mode switch messages

_SYSEX_ID = 0x01 # tags a SysEx message as one of ours (a sub-mode switch) vs any other SysEx a script might see
_DATA_BYTE_COUNT = 3 # 21 bits for data

def EncodeSubModeSwitch(key: int, data: int | None) -> bytes:
    """
    Pack a McuCompositeMode sub-mode switch (key + an optional accompanying value of any size, e.g. a
    channel index) into one complete SysEx message (0xF0 ... 0xF7).
    """
    hasData = 1 if data is not None else 0
    value = data if data is not None else 0
    valueBytes = []
    remaining = value
    for _ in range(_DATA_BYTE_COUNT):
        valueBytes.append(remaining & 0x7F)
        remaining >>= 7
    return bytes([0xF0, _SYSEX_ID, key & 0x03, hasData, *valueBytes, 0xF7])

def DecodeSubModeSwitch(sysexBytes: bytes) -> tuple[int, int | None] | None:
    """
    Inverse of EncodeSubModeSwitch. Returns None if sysexBytes isn't one of our messages (wrong id, length,
    or framing).
    """
    if (len(sysexBytes) != _DATA_BYTE_COUNT + 5
            or sysexBytes[0] != 0xF0 or sysexBytes[1] != _SYSEX_ID or sysexBytes[-1] != 0xF7):
        return None
    key = sysexBytes[2]
    hasData = sysexBytes[3]
    value = 0
    for i in range(_DATA_BYTE_COUNT):
        value |= sysexBytes[4 + i] << (7 * i)
    return key, (value if hasData else None)
