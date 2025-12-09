from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from OLD.utils import get_gps_from_image

from ..extensions import db
from ..models import Imagery
from .storage_service import StorageService


class ImageryService:
    def __init__(self, session, storage: StorageService):
        self.session = session
        self.storage = storage
        self.storage.ensure_directories()

    def _parse_datetime(self, value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    def _parse_float(self, value: Optional[str]) -> Optional[float]:
        if value in (None, ""):
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def create_from_upload(
        self,
        file: FileStorage,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Imagery:
        if not file or not file.filename:
            raise ValueError("Файл изображения обязателен")

        metadata = metadata or {}
        original_name = secure_filename(file.filename) or f"{uuid4().hex}.img"
        stored_name = f"{uuid4().hex}_{original_name}"
        relative_path = self.storage.save_file(file, "imagery", stored_name)
        absolute_path = self.storage.absolute_path(relative_path)

        gps = get_gps_from_image(absolute_path)

        imagery = Imagery(
            original_filename=original_name,
            stored_path=relative_path,
            captured_at=self._parse_datetime(metadata.get("captured_at")),
            gps_lat=self._parse_float(metadata.get("gps_lat")) or (gps.get("latitude") if gps else None),
            gps_lon=self._parse_float(metadata.get("gps_lon")) or (gps.get("longitude") if gps else None),
            metadata={k: v for k, v in metadata.items() if k not in {"gps_lat", "gps_lon", "captured_at"}},
        )

        self.session.add(imagery)
        self.session.commit()
        return imagery

    def list_imagery(self):
        return Imagery.query.order_by(Imagery.created_at.desc()).all()

    def get(self, imagery_id: str) -> Imagery:
        return Imagery.query.get_or_404(imagery_id)

