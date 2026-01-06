"""Application-level settings shared across UI widgets."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Any

from resources import CROP_THRESHOLDS

from .observer import Observable
from .singleton import SingletonMeta


@dataclass
class AnalysisOptions:
    """Structured representation of analysis knobs."""

    crop: str
    stress: float
    veg: float
    auto_boundaries: bool = False
    enhance_contrast: bool = False
    multispectral: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AppSettings(Observable, metaclass=SingletonMeta):
    """Singleton + Observer: keeps UI language/options in sync application-wide."""

    def __init__(self):
        super().__init__()
        default_crop = list(CROP_THRESHOLDS.keys())[0]
        self._language = "Русский"
        self._analysis_options = AnalysisOptions(
            crop=default_crop,
            stress=CROP_THRESHOLDS[default_crop]["stressed"],
            veg=CROP_THRESHOLDS[default_crop]["healthy"],
        )

    @property
    def language(self) -> str:
        return self._language

    def set_language(self, language: str) -> None:
        if language != self._language:
            self._language = language
            self.notify("language_changed", language)

    @property
    def analysis_options(self) -> AnalysisOptions:
        return self._analysis_options

    def update_analysis_options(self, payload: Dict[str, Any]) -> None:
        self._analysis_options = AnalysisOptions(**payload)
        self.notify("analysis_options_updated", self._analysis_options)

    def as_dialog_payload(self) -> Dict[str, Any]:
        return self._analysis_options.to_dict()
