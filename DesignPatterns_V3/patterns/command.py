"""Command objects that drive the analysis pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np

from .settings import AnalysisOptions


@dataclass
class AnalysisContext:
    """Aggregates mutable state that commands operate on."""

    source_path: str
    options: Optional[AnalysisOptions]
    index_type: str = "NDVI_emp"
    image: Optional[np.ndarray] = None
    indices: Optional[dict] = None
    index_map: Optional[np.ndarray] = None
    heatmap_path: Optional[str] = None
    stats: Optional[dict] = None
    conclusion: Optional[str] = None


class AnalysisCommand:
    """Command interface."""

    def execute(self, ctx: AnalysisContext) -> None:
        raise NotImplementedError


class LoadImageryCommand(AnalysisCommand):
    """Loads imagery into the context."""

    def __init__(self, loader):
        self.loader = loader

    def execute(self, ctx: AnalysisContext) -> None:
        ctx.image = self.loader(ctx.source_path, ctx.options)


class ComputeIndicesCommand(AnalysisCommand):
    """Computes vegetation indices."""

    def __init__(self, calculator):
        self.calculator = calculator

    def execute(self, ctx: AnalysisContext) -> None:
        ctx.indices = self.calculator(ctx.image)
        if ctx.index_type not in ctx.indices:
            raise ValueError(f"Индекс {ctx.index_type} не поддерживается")
        ctx.index_map = ctx.indices[ctx.index_type]


class GenerateHeatmapCommand(AnalysisCommand):
    """Creates a heatmap file for the selected index."""

    def __init__(self, heatmap_fn):
        self.heatmap_fn = heatmap_fn

    def execute(self, ctx: AnalysisContext) -> None:
        if ctx.index_map is None:
            raise RuntimeError("Нет данных индекса для построения тепловой карты")
        output = ctx.heatmap_path
        if not output:
            output_dir = Path("assets")
            output_dir.mkdir(exist_ok=True)
            output = output_dir / "heatmap_temp.png"
        self.heatmap_fn(ctx.index_map, str(output))
        ctx.heatmap_path = str(output)


class ClassifyFieldCommand(AnalysisCommand):
    """Derives distribution stats and conclusion."""

    def __init__(self, classifier):
        self.classifier = classifier

    def execute(self, ctx: AnalysisContext) -> None:
        stats, conclusion = self.classifier(ctx.index_map)
        ctx.stats = stats
        ctx.conclusion = conclusion
