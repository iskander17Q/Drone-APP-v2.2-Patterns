"""Facade that orchestrates analysis workflows for UI and backend."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import matplotlib.pyplot as plt
import numpy as np

from analysis import load_image
from image_processing import classify_index, generate_heatmap
from resources import SPECTRAL_INDEX_DESCRIPTIONS
from utils import generate_pdf_report

from .command import (
    AnalysisContext,
    ClassifyFieldCommand,
    ComputeIndicesCommand,
    GenerateHeatmapCommand,
    LoadImageryCommand,
)
from .image_loader import build_loader
from .indices import SpectralIndexCalculator
from .settings import AnalysisOptions, AppSettings


@dataclass
class AnalysisResult:
    heatmap_path: str
    stats: Dict[str, float]
    conclusion: str
    index_map: np.ndarray
    indices: Dict[str, np.ndarray]
    index_type: str


class AnalysisFacade:
    """Provides a single entrypoint for orchestrating image analysis."""

    def __init__(self, calculator: SpectralIndexCalculator | None = None):
        self.calculator = calculator or SpectralIndexCalculator()

    def _ensure_options(self, options) -> AnalysisOptions:
        if options is None:
            return AppSettings().analysis_options
        if isinstance(options, AnalysisOptions):
            return options
        return AnalysisOptions(**options)

    def _commands(self):
        return [
            LoadImageryCommand(build_loader),
            ComputeIndicesCommand(self.calculator.compute_all),
            GenerateHeatmapCommand(generate_heatmap),
            ClassifyFieldCommand(classify_index),
        ]

    def analyze_image(
        self,
        file_path: str,
        *,
        index_type: str = "NDVI_emp",
        options: AnalysisOptions | dict | None = None,
        heatmap_path: Optional[str] = None,
    ) -> AnalysisResult:
        opts = self._ensure_options(options)
        ctx = AnalysisContext(
            source_path=file_path,
            options=opts,
            index_type=index_type,
            heatmap_path=heatmap_path,
        )
        for command in self._commands():
            command.execute(ctx)

        return AnalysisResult(
            heatmap_path=ctx.heatmap_path,
            stats=ctx.stats or {},
            conclusion=ctx.conclusion or "",
            index_map=ctx.index_map,
            indices=ctx.indices or {},
            index_type=index_type,
        )

    def export_report(
        self,
        pdf_path: str,
        result: AnalysisResult,
        original_image_path: str,
        report_text: Optional[str] = None,
        gps: Optional[Dict] = None,
    ):
        """Builder-driven PDF export used in UI and backend workflows."""
        text = report_text or self._format_report_text(result)
        generate_pdf_report(
            pdf_path,
            original_image_path,
            result.heatmap_path,
            text,
            gps,
            index_type=result.index_type,
        )

    def export_indices(
        self,
        image_path: str,
        export_dir: str,
        *,
        options: AnalysisOptions | dict | None = None,
    ):
        """Creates per-index heatmaps and annotated previews."""
        opts = self._ensure_options(options)
        image = load_image(image_path, options=opts)
        indices = self.calculator.compute_all(image.astype("float32"))

        export_root = Path(export_dir)
        export_root.mkdir(parents=True, exist_ok=True)
        readme_lines = ["СПЕКТРАЛЬНЫЕ КАРТЫ:\n"]

        for index_name, index_map in indices.items():
            heatmap_path = export_root / f"{index_name}.png"
            generate_heatmap(index_map, str(heatmap_path))
            desc = self._lookup_description(index_name)
            self._render_index_description(export_root, index_name, index_map, desc)
            readme_lines.append(self._format_readme_entry(index_name, desc))

        readme_lines.append(
            "\nКаждый PNG-файл — визуализация конкретного индекса. Файлы *_desc.png "
            "содержат ту же карту с кратким описанием показателя."
        )
        with open(export_root / "README.txt", "w", encoding="utf-8") as handle:
            handle.write("\n".join(readme_lines))

    @staticmethod
    def _format_report_text(result: AnalysisResult) -> str:
        lines = ["Распределение состояния растений:"]
        for category, pct in (result.stats or {}).items():
            lines.append(f"{category}: {pct:.1f}%")
        lines.append("")
        lines.append(f"Вывод: {result.conclusion}")
        return "\n".join(lines)

    @staticmethod
    def _lookup_description(index_name: str):
        normalized = (
            index_name.lower()
            .replace("_emp", "")
            .replace("cive", "civi")
            .replace("exg", "exg")
            .replace("mgrvi", "mgrvi")
            .replace("ndvi", "ndvi")
        )
        for key, value in SPECTRAL_INDEX_DESCRIPTIONS.items():
            if key.lower() == normalized:
                return value
        return None

    def _render_index_description(self, export_root: Path, index_name: str, index_map, desc):
        plt.figure(figsize=(10, 6))
        plt.imshow(index_map, cmap="RdYlGn")
        plt.title(desc["name"] if desc else index_name)
        plt.colorbar(label="Значение индекса")
        plt.axis("off")
        if desc and desc.get("description"):
            plt.figtext(
                0.5,
                0.01,
                f"{desc['name']}\n\n{desc['description']}",
                wrap=True,
                fontsize=9,
                ha="center",
                va="bottom",
                bbox={"facecolor": "white", "alpha": 0.7, "pad": 6},
            )
        desc_path = export_root / f"{index_name}_desc.png"
        plt.savefig(desc_path, bbox_inches="tight", dpi=200)
        plt.close()

    @staticmethod
    def _format_readme_entry(index_name: str, desc):
        if desc and desc.get("description"):
            return f"{index_name}: {desc['name']}\n{desc['description']}\n"
        return f"{index_name}\n"
