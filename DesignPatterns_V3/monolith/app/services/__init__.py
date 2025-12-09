from flask import current_app

from ..extensions import db
from .analysis_service import AnalysisService
from .imagery_service import ImageryService
from .report_service import ReportService
from .storage_service import StorageService


def get_storage_service() -> StorageService:
    storage_service: StorageService = current_app.extensions.get("storage_service")
    if not storage_service:
        storage_service = StorageService(current_app.config["STORAGE_ROOT"])
        current_app.extensions["storage_service"] = storage_service
    return storage_service


def get_imagery_service() -> ImageryService:
    return ImageryService(db.session, get_storage_service())


def get_analysis_service() -> AnalysisService:
    return AnalysisService(db.session, get_storage_service())


def get_report_service() -> ReportService:
    return ReportService(db.session, get_storage_service())

