"""Facade that hides the details of the analysis pipeline."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import numpy as np

from analysis import (
    classify_index,
    compute_indices,
    generate_heatmap,
    load_image,
)
from resources import SPECTRAL_INDEX_DESCRIPTIONS
from utils import generate_pdf_report

from .command import (
    AnalysisContext,
    ClassifyFieldCommand,
    ComputeIndicesCommand,
    GenerateHeatmapCommand,
    LoadImageryCommand,
)
from .settings import AnalysisOptions


@dataclass
class AnalysisResult:
    heatmap_path: str
    stats: Dict[str, float]
    conclusion: str
    indices: Dict[str, np.ndarray]
    index_map: np.ndarray
    index_type: str


class AnalysisFacade:
    """Facade used by UI and background services."""

    def __init__(self):
        self._load_command = LoadImageryCommand(lambda path, opts: load_image(path, options=opts))
        self._compute_command = ComputeIndicesCommand(compute_indices)
        self._heatmap_command = GenerateHeatmapCommand(generate_heatmap)
        self._classify_command = ClassifyFieldCommand(classify_index)

    def analyze_image(
        self,
        image_path: str,
        index_type: str = "NDVI_emp",
        options: Optional[AnalysisOptions] = None,
        heatmap_path: Optional[str] = None,
    ) -> AnalysisResult:
        ctx = AnalysisContext(
            source_path=image_path,
            options=options,
            index_type=index_type,
            heatmap_path=heatmap_path,
        )
        for command in (
            self._load_command,
            self._compute_command,
            self._heatmap_command,
            self._classify_command,
        ):
            command.execute(ctx)
        return AnalysisResult(
            heatmap_path=ctx.heatmap_path,
            stats=ctx.stats or {},
            conclusion=ctx.conclusion or "",
            indices=ctx.indices or {},
            index_map=ctx.index_map,
            index_type=index_type,
        )

    def export_report(
        self,
        pdf_path: str,
        result: AnalysisResult,
        original_image_path: str,
        report_text: str,
        gps: Optional[Dict] = None,
    ) -> None:
        generate_pdf_report(
            pdf_path,
            original_image_path,
            result.heatmap_path,
            report_text,
            gps,
            index_type=result.index_type,
        )

    def export_indices(
        self,
        image_path: str,
        export_dir: str,
        options: Optional[AnalysisOptions] = None,
    ) -> str:
        """Сохраняет все спектральные карты и описания, возвращает путь к README."""
        image = load_image(image_path, options=options)
        indices = compute_indices(image)
        os.makedirs(export_dir, exist_ok=True)
        readme_lines = ["СПЕКТРАЛЬНЫЕ КАРТЫ:\n"]
        for index_name, index_map in indices.items():
            output_path = os.path.join(export_dir, f"{index_name}.png")
            generate_heatmap(index_map, output_path)
            desc = self._find_description(index_name)
            self._save_index_description(export_dir, index_name, index_map, desc)
            if desc:
                readme_lines.append(f"{index_name}: {desc['name']}\n{desc['description']}\n")
            else:
                readme_lines.append(f"{index_name}\n")
        readme_lines.append(
            "\nКаждый PNG-файл — визуализация индекса. *_desc.png включает подписи и пояснения."
        )
        readme_path = os.path.join(export_dir, "README.txt")
        with open(readme_path, "w", encoding="utf-8") as handler:
            handler.write("\n".join(readme_lines))
        return readme_path

    def _find_description(self, index_name: str):
        normalized = (
            index_name.lower()
            .replace("_emp", "")
            .replace("cive", "civi")
        )
        for key, desc in SPECTRAL_INDEX_DESCRIPTIONS.items():
            if key.lower() == normalized:
                return desc
        return None

    def _save_index_description(self, export_dir: str, index_name: str, index_map, desc):
        import matplotlib.pyplot as plt

        plt.figure(figsize=(10, 6))
        plt.imshow(index_map, cmap="RdYlGn")
        plt.title(desc["name"] if desc else index_name)
        plt.colorbar(label="Значение индекса")
        plt.axis("off")
        if desc and desc.get("description"):
            description = f"{desc['name']}\n\n{desc['description']}"
            plt.figtext(
                0.5,
                0.01,
                description,
                wrap=True,
                fontsize=9,
                ha="center",
                va="bottom",
                bbox={"facecolor": "white", "alpha": 0.7, "pad": 6},
            )
        desc_path = os.path.join(export_dir, f"{index_name}_desc.png")
        plt.savefig(desc_path, bbox_inches="tight", dpi=200)
        plt.close()
