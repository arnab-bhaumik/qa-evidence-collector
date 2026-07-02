from __future__ import annotations

from typing import Callable

from pynput import keyboard


class HotkeyManager:
    def __init__(self) -> None:
        self._listener: keyboard.GlobalHotKeys | None = None
        self._callback: Callable | None = None
        self._hotkey: str = ""

    def register(self, hotkey: str, callback: Callable) -> None:
        self.unregister()
        self._hotkey = hotkey
        self._callback = callback
        try:
            self._listener = keyboard.GlobalHotKeys({hotkey: callback})
            self._listener.start()
        except Exception:
            self._listener = None

    def unregister(self) -> None:
        if self._listener:
            try:
                self._listener.stop()
            except Exception:
                pass
            self._listener = None

    @property
    def active_hotkey(self) -> str:
        return self._hotkey if self._listener else ""
