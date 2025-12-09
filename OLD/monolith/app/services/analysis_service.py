from typing import Dict, Optional

from flask import current_app

from OLD.image_processing import (
    classify_index,
    compute_indices,
    generate_heatmap,
    load_image,
)

from ..models import AnalysisRun, Heatmap, Imagery
from .storage_service import StorageService


class AnalysisService:
    def __init__(self, session, storage: StorageService):
        self.session = session
        self.storage = storage

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

        imagery_path = self.storage.absolute_path(run.imagery.stored_path)
        image = load_image(imagery_path)
        indices = compute_indices(image)

        index_type = run.index_type or "NDVI_emp"
        if index_type not in indices:
            raise ValueError(f"Индекс {index_type} не был вычислен")

        index_map = indices[index_type]
        heatmap_filename = f"{run.id}_{index_type}.png"
        heatmap_relative = self.storage.build_relative("heatmaps", heatmap_filename)
        heatmap_absolute = self.storage.absolute_path(heatmap_relative)
        generate_heatmap(index_map, heatmap_absolute)

        heatmap = Heatmap(
            analysis_run=run,
            index_type=index_type,
            file_path=heatmap_relative,
            min_value=float(index_map.min()),
            max_value=float(index_map.max()),
        )
        self.session.add(heatmap)

        distribution, conclusion = classify_index(index_map)
        stats = {
            "distribution": distribution,
            "conclusion": conclusion,
            "min": float(index_map.min()),
            "max": float(index_map.max()),
            "mean": float(index_map.mean()),
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

