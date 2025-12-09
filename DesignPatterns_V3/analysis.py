import cv2
import numpy as np

from patterns.image_loader import build_loader
from patterns.indices import SpectralIndexCalculator
from patterns.settings import AnalysisOptions

_calculator = SpectralIndexCalculator()


def load_image(file_path, options: AnalysisOptions | None = None):
    """
    Загружает изображение из файла, применяя декораторы в зависимости от настроек.
    """
    loader = build_loader(options)
    return loader.load(file_path)

def compute_indices(image):
    """
    Вычисляет набор индексов растительности на основе выбранной стратегии.
    """
    return _calculator.compute_all(image.astype("float32"))

def generate_heatmap(index_map, output_path):
    """
    Генерирует тепловую карту на основе матрицы индекса:
    - Нормализует значения к [0..1]
    - Конвертирует в [0..255]
    - Применяет цветовую карту COLORMAP_JET
    - Сохраняет в output_path (в формате PNG)
    """
    idx_min = np.nanmin(index_map)
    idx_max = np.nanmax(index_map)
    # Нормализация
    norm = (index_map - idx_min) / (idx_max - idx_min + 1e-6)
    norm_uint8 = (norm * 255).astype('uint8')
    
    heatmap_bgr = cv2.applyColorMap(norm_uint8, cv2.COLORMAP_JET)
    # Переводим в RGB для корректного сохранения цветов
    heatmap_rgb = cv2.cvtColor(heatmap_bgr, cv2.COLOR_BGR2RGB)
    cv2.imwrite(output_path, heatmap_rgb)

def classify_index(index_map):
    """
    Классифицирует состояние растительности по значению индекса.
    (Пороговые значения скорректированы, чтобы поле не считалось слишком "критичным".)
    
    Категории:
      - Здоровые: > 0.1
      - Легкий стресс: 0.0 .. 0.1
      - Сильный стресс: -0.1 .. 0.0
      - Критическое: < -0.1
      
    Возвращает (stats, conclusion):
      stats = { "Здоровые": float, "Легкий стресс": float, ... }
      conclusion = "..."
    """
    total_pixels = index_map.size
    if total_pixels == 0:
        return {}, "Нет данных для анализа"
    
    healthy_mask = index_map > 0.1
    mild_mask = (index_map > 0.0) & (index_map <= 0.1)
    stress_mask = (index_map > -0.1) & (index_map <= 0.0)
    critical_mask = index_map <= -0.1
    
    healthy_pct = np.sum(healthy_mask) / total_pixels * 100.0
    mild_pct = np.sum(mild_mask) / total_pixels * 100.0
    stress_pct = np.sum(stress_mask) / total_pixels * 100.0
    critical_pct = np.sum(critical_mask) / total_pixels * 100.0
    
    stats = {
        "Здоровые": healthy_pct,
        "Легкий стресс": mild_pct,
        "Сильный стресс": stress_pct,
        "Критическое": critical_pct
    }
    
    # Выбираем основную категорию по максимуму
    main_cat = max(stats, key=stats.get)
    
    if main_cat == "Здоровые":
        conclusion = "Большая часть поля здорова, но встречаются участки стресса."
    elif main_cat == "Легкий стресс":
        conclusion = "Преобладает легкий стресс, возможно небольшое ухудшение состояния."
    elif main_cat == "Сильный стресс":
        conclusion = "Многие участки поля находятся в сильном стрессе. Требуются меры."
    else:  # main_cat == "Критическое"
        conclusion = "Поле в критическом состоянии или отсутствует растительность."
    
    return stats, conclusion
