"""Strategy + Factory for spectral index calculations."""

from __future__ import annotations

from typing import Dict, Type, List

import numpy as np


class SpectralIndexStrategy:
    """Strategy interface for a single vegetation index."""

    name = ""

    def compute(self, image: np.ndarray) -> np.ndarray:
        raise NotImplementedError


class NdviStrategy(SpectralIndexStrategy):
    name = "NDVI_emp"

    def compute(self, image: np.ndarray) -> np.ndarray:
        g = image[:, :, 1].astype("float32")
        r = image[:, :, 0].astype("float32")
        return (g - r) / (g + r + 1e-6)


class VariStrategy(SpectralIndexStrategy):
    name = "VARI"

    def compute(self, image: np.ndarray) -> np.ndarray:
        g = image[:, :, 1].astype("float32")
        r = image[:, :, 0].astype("float32")
        b = image[:, :, 2].astype("float32")
        return (g - r) / (g + r - b + 1e-6)


class GliStrategy(SpectralIndexStrategy):
    name = "GLI"

    def compute(self, image: np.ndarray) -> np.ndarray:
        g = image[:, :, 1].astype("float32")
        r = image[:, :, 0].astype("float32")
        b = image[:, :, 2].astype("float32")
        return (2 * g - r - b) / (2 * g + r + b + 1e-6)


class ExgStrategy(SpectralIndexStrategy):
    name = "ExG"

    def compute(self, image: np.ndarray) -> np.ndarray:
        g = image[:, :, 1].astype("float32")
        r = image[:, :, 0].astype("float32")
        b = image[:, :, 2].astype("float32")
        return 2 * g - r - b


class CiveStrategy(SpectralIndexStrategy):
    name = "CIVE"

    def compute(self, image: np.ndarray) -> np.ndarray:
        r = image[:, :, 0].astype("float32")
        g = image[:, :, 1].astype("float32")
        b = image[:, :, 2].astype("float32")
        return 0.441 * r - 0.881 * g + 0.385 * b + 18.78745


class MgrviStrategy(SpectralIndexStrategy):
    name = "MGRVI"

    def compute(self, image: np.ndarray) -> np.ndarray:
        r = image[:, :, 0].astype("float32")
        g = image[:, :, 1].astype("float32")
        return (g ** 2 - r ** 2) / (g ** 2 + r ** 2 + 1e-6)


class IndexCalculatorFactory:
    """Factory that returns strategy instances by name."""

    def __init__(self):
        self._registry: Dict[str, Type[SpectralIndexStrategy]] = {
            cls.name: cls
            for cls in [
                NdviStrategy,
                VariStrategy,
                GliStrategy,
                ExgStrategy,
                CiveStrategy,
                MgrviStrategy,
            ]
        }

    def create(self, name: str) -> SpectralIndexStrategy:
        strategy_cls = self._registry.get(name)
        if not strategy_cls:
            raise KeyError(f"Неизвестный индекс: {name}")
        return strategy_cls()

    def available_indices(self) -> List[str]:
        return list(self._registry.keys())


class SpectralIndexCalculator:
    """Helper that evaluates all requested strategies."""

    def __init__(self, factory: IndexCalculatorFactory | None = None):
        self.factory = factory or IndexCalculatorFactory()

    def compute_all(self, image: np.ndarray) -> Dict[str, np.ndarray]:
        indices = {}
        for name in self.factory.available_indices():
            strategy = self.factory.create(name)
            indices[name] = strategy.compute(image)
        return indices
