from typing import Dict, Optional

from flask import current_app

from patterns import AnalysisFacade
from patterns.settings import AnalysisOptions

from ..models import AnalysisRun, Heatmap, Imagery
from .storage_service import StorageService


class AnalysisService:
    def __init__(self, session, storage: StorageService):
        self.session = session
        self.storage = storage
        self.facade = AnalysisFacade()

    def create_run(
        self,
        imagery: Imagery,
        index_type: str = "NDVI_emp",
        options: Optional[Dict] = None,
    ) -> AnalysisRun:
        run = AnalysisRun(
            imagery=imagery,
            index_type=index_type or "NDVI_emp",
            status="pending",
            options=options or {},
        )
        self.session.add(run)
        self.session.commit()
        return run

    def perform_run(self, run_id: str) -> AnalysisRun:
        run = AnalysisRun.query.get(run_id)
        if not run:
            raise ValueError(f"AnalysisRun {run_id} не найден")

        if run.status in {"completed", "running"}:
            return run

        run.status = "running"
        self.session.commit()

        index_type = run.index_type or "NDVI_emp"
        heatmap_filename = f"{run.id}_{index_type}.png"
        heatmap_relative = self.storage.build_relative("heatmaps", heatmap_filename)
        heatmap_absolute = self.storage.absolute_path(heatmap_relative)
        result = self.facade.analyze_image(
            self.storage.absolute_path(run.imagery.stored_path),
            index_type=index_type,
            options=self._options_from_payload(run.options),
            heatmap_path=heatmap_absolute,
        )

        heatmap = Heatmap(
            analysis_run=run,
            index_type=index_type,
            file_path=heatmap_relative,
            min_value=float(result.index_map.min()),
            max_value=float(result.index_map.max()),
        )
        self.session.add(heatmap)
        stats = {
            "distribution": result.stats,
            "conclusion": result.conclusion,
            "min": float(result.index_map.min()),
            "max": float(result.index_map.max()),
            "mean": float(result.index_map.mean()),
        }
        run.stats = stats
        run.status = "completed"
        run.error_message = None
        self.session.commit()

        current_app.logger.info("Анализ %s завершён", run.id)
        return run

    def mark_failed(self, run_id: str, message: str):
        run = AnalysisRun.query.get(run_id)
        if not run:
            return
        run.status = "failed"
        run.error_message = message
        self.session.commit()

    def _options_from_payload(self, payload) -> AnalysisOptions | None:
        if not payload:
            return None
        try:
            return AnalysisOptions(**payload)
        except TypeError:
            return None
