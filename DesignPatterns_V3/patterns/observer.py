"""Observer helpers to propagate UI events."""

from __future__ import annotations

from typing import Protocol, Any, List


class SettingsObserver(Protocol):
    """Interface for classes that react to AppSettings events."""

    def update(self, event: str, payload: Any) -> None:
        ...


class Observable:
    """Small observable mixin used by the AppSettings singleton."""

    def __init__(self):
        self._observers: List[SettingsObserver] = []

    def register(self, observer: SettingsObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def unregister(self, observer: SettingsObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event: str, payload: Any = None) -> None:
        for observer in list(self._observers):
            observer.update(event, payload)
