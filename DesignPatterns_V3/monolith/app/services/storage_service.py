import os
from pathlib import Path
from typing import BinaryIO, Optional
from uuid import uuid4


class StorageService:
    """Простое файловое хранилище с возможностью замены на MinIO."""

    def __init__(self, root_path: str):
        self.root = Path(root_path).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _ensure_subdir(self, subdir: str) -> Path:
        target = self.root / subdir
        target.mkdir(parents=True, exist_ok=True)
        return target

    def save_file(
        self,
        file_obj: BinaryIO,
        subdir: str,
        filename: Optional[str] = None,
    ) -> str:
        safe_name = filename or uuid4().hex
        target_dir = self._ensure_subdir(subdir)
        target_path = target_dir / safe_name

        if hasattr(file_obj, "save"):
            file_obj.save(target_path)
        else:
            with open(target_path, "wb") as out:
                out.write(file_obj.read())

        return str(target_path.relative_to(self.root))

    def absolute_path(self, relative_path: str) -> str:
        return str((self.root / relative_path).resolve())

    def build_relative(self, subdir: str, filename: str) -> str:
        self._ensure_subdir(subdir)
        return str(Path(subdir) / filename)

    def ensure_directories(self):
        for sub in ("imagery", "heatmaps", "reports"):
            self._ensure_subdir(sub)

    def exists(self, relative_path: str) -> bool:
        return (self.root / relative_path).exists()

    def delete(self, relative_path: str):
        path = self.root / relative_path
        if path.exists():
            path.unlink()


