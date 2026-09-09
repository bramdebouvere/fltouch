from behaviors.mcu_base_behavior import McuBaseBehavior
from utilities.fl_class_import import FlMidiMsg
from device_hal.mcu_device import McuDevice
from modes.mcu_base_mode import McuBaseMode
from utilities.sub_mode_switch_sysex import DecodeSubModeSwitch

class McuCompositeMode(McuBaseMode):
    """
    A mode that contains multiple sub-modes, each a full McuBaseMode.

    Owns permanent behaviors (always active) plus a registry of sub-modes keyed by integer.
    Handles switching between sub-modes and keeps modes in sync over MIDI across the main unit and extenders.

    Subclasses override OnModeSwitch to react to transition data before the sub-mode enables.
    """

    def __init__(self, device: McuDevice, permanentBehaviors: list[McuBaseBehavior]):
        super().__init__(device, permanentBehaviors, None)  # composite has no own banking manager, implemented by sub-modes if needed
        self._subModes = {} # key (int) -> McuBaseMode
        self._activeSubMode = None
        self._activeSubModeKey = -1

    def _addSubMode(self, key: int, mode: McuBaseMode):
        """Register a sub-mode under the given integer key."""
        self._subModes[key] = mode

    # -------------------------------------------------------
    # Public switching API (called by behaviors or sub-modes)
    # -------------------------------------------------------

    def SwitchTo(self, key: int, data:int|None=None):
        """Switch to the sub-mode identified by key, carrying an optional data value of any size (sent via
        SysEx — see utilities/sub_mode_switch_sysex.py)."""
        if self.McuDevice.isExtender:
            # Extenders request via MIDI; the main coordinates and re-broadcasts
            self._dispatchSwitch(key, data)
        else:
            self._coordinateSwitch(key, data)

    # --------------------------
    # Internal switching helpers
    # --------------------------

    def _coordinateSwitch(self, key: int, data:int|None=None):
        """Main unit: broadcast to all receivers first, then apply locally."""
        self._dispatchSwitch(key, data)
        self._applySwitch(key, data)

    def _dispatchSwitch(self, key: int, data:int|None=None):
        """Send the sub-mode switch to all dispatch receivers."""
        self.McuDevice.SendSubModeSwitchToExtender(key, data)

    def _applySwitch(self, key: int, data:int|None=None):
        """Disable the current sub-mode, call the transition hook, then enable the new sub-mode."""
        if self._activeSubMode is not None:
            self._activeSubMode.OnDisable()
        self.OnModeSwitch(key, data)
        self._activeSubModeKey = key
        self._activeSubMode = self._subModes[key]
        self._activeSubMode.OnEnable()

    # -------------------
    # Hook for subclasses
    # -------------------

    def OnModeSwitch(self, key: int, data: int|None):
        """Called between disabling the old sub-mode and enabling the new one.
        Override to update shared state before the incoming sub-mode's OnEnable runs."""
        pass

    # -------------------------------
    # McuBaseMode lifecycle overrides
    # -------------------------------

    def OnEnable(self):
        super().OnEnable()  # enables permanent behaviors
        defaultKey = next(iter(self._subModes))
        self._applySwitch(defaultKey)

    def OnDisable(self):
        if self._activeSubMode is not None:
            self._activeSubMode.OnDisable()
            self._activeSubMode = None
            self._activeSubModeKey = -1
        super().OnDisable()  # disables permanent behaviors

    # ----------------------------------------------------------
    # FL Studio callbacks: permanent behaviors & active sub-mode
    # ----------------------------------------------------------

    def OnMidiMsg(self, event: FlMidiMsg):
        if not self._enabled:
            return
        super().OnMidiMsg(event)
        if self._activeSubMode is not None:
            self._activeSubMode.OnMidiMsg(event)

    def OnRefresh(self, flags):
        super().OnRefresh(flags)
        if self._activeSubMode is not None:
            self._activeSubMode.OnRefresh(flags)

    def OnDirtyMixerTrack(self, SetTrackNum):
        super().OnDirtyMixerTrack(SetTrackNum)
        if self._activeSubMode is not None:
            self._activeSubMode.OnDirtyMixerTrack(SetTrackNum)

    def OnDirtyChannel(self, index):
        super().OnDirtyChannel(index)
        if self._activeSubMode is not None:
            self._activeSubMode.OnDirtyChannel(index)

    def OnUpdateMeters(self):
        super().OnUpdateMeters()
        if self._activeSubMode is not None:
            self._activeSubMode.OnUpdateMeters()

    def OnIdle(self):
        super().OnIdle()
        if self._activeSubMode is not None:
            self._activeSubMode.OnIdle()

    def OnSendTempMsg(self, msg: str, duration=2000):
        super().OnSendTempMsg(msg, duration)
        if self._activeSubMode is not None:
            self._activeSubMode.OnSendTempMsg(msg, duration)

    def OnSysEx(self, event: FlMidiMsg):
        switchData = DecodeSubModeSwitch(bytes(event.sysex)) if event.sysex else None

        # check if switchData is valid and the key points to an actual submode
        if switchData is not None and switchData[0] in self._subModes:
            key, data = switchData
            if self.McuDevice.isExtender:
                self._applySwitch(key, data)
            else:
                self._coordinateSwitch(key, data)
            event.handled = True
            return event
        super().OnSysEx(event)
        if self._activeSubMode is not None:
            self._activeSubMode.OnSysEx(event)

    def OnFirstConnect(self):
        super().OnFirstConnect()
        if self._activeSubMode is not None:
            self._activeSubMode.OnFirstConnect()

    def OnProjectLoad(self, status: int):
        super().OnProjectLoad(status)
        if self._activeSubMode is not None:
            self._activeSubMode.OnProjectLoad(status)

    def OnUpdateBeatIndicator(self, value: int):
        super().OnUpdateBeatIndicator(value)
        if self._activeSubMode is not None:
            self._activeSubMode.OnUpdateBeatIndicator(value)

    def OnWaitingForInput(self):
        super().OnWaitingForInput()
        if self._activeSubMode is not None:
            self._activeSubMode.OnWaitingForInput()
