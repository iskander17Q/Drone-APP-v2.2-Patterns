"""Proxy objects for infrastructure components."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Protocol, BinaryIO, Optional

logger = logging.getLogger(__name__)


class StorageLike(Protocol):
    """Protocol to avoid tight coupling with concrete storage implementation."""

    root: Path

    def save_file(
        self,
        file_obj: BinaryIO,
        subdir: str,
        filename: Optional[str] = None,
    ) -> str:
        ...

    def absolute_path(self, relative_path: str) -> str:
        ...

    def build_relative(self, subdir: str, filename: str) -> str:
        ...

    def ensure_directories(self):
        ...

    def exists(self, relative_path: str) -> bool:
        ...

    def delete(self, relative_path: str):
        ...


class StorageProxy:
    """
    Proxy around the storage layer.

    - Валидирует относительные пути, чтобы они не выходили за пределы корневой директории.
    - Логирует операции чтения/записи, чтобы было проще отслеживать работу сервиса.
    - Делегирует фактическое чтение/запись объекту StorageService без модификации его кода.
    """

    def __init__(self, storage: StorageLike):
        self._storage = storage
        self._root = Path(storage.root).resolve()

    def save_file(
        self,
        file_obj: BinaryIO,
        subdir: str,
        filename: Optional[str] = None,
    ) -> str:
        relative = self._storage.save_file(file_obj, subdir, filename)
        self._assert_inside_root(relative)
        logger.info("Файл сохранён в %s/%s", subdir, relative)
        return relative

    def absolute_path(self, relative_path: str) -> str:
        self._assert_inside_root(relative_path)
        return self._storage.absolute_path(relative_path)

    def build_relative(self, subdir: str, filename: str) -> str:
        relative = self._storage.build_relative(subdir, filename)
        self._assert_inside_root(relative)
        return relative

    def ensure_directories(self):
        return self._storage.ensure_directories()

    def exists(self, relative_path: str) -> bool:
        self._assert_inside_root(relative_path)
        return self._storage.exists(relative_path)

    def delete(self, relative_path: str):
        self._assert_inside_root(relative_path)
        logger.info("Удаление файла %s", relative_path)
        return self._storage.delete(relative_path)

    def _assert_inside_root(self, relative_path: str):
        candidate = (self._root / relative_path).resolve()
        if not str(candidate).startswith(str(self._root)):
            raise ValueError(f"Путь {relative_path} выходит за пределы {self._root}")
