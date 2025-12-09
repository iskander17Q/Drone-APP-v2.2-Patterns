import cv2
import numpy as np
import rawpy

def load_image(file_path):
    """
    Загружает изображение из файла.
    Поддерживаемые форматы: JPG, PNG, BMP и RAW (через rawpy).
    Возвращает numpy-массив формата (H, W, 3) в RGB.
    """
    file_path_lower = file_path.lower()
    if file_path_lower.endswith(('.raw', '.dng', '.nef', '.cr2', '.arw')):
        with rawpy.imread(file_path) as raw:
            rgb = raw.postprocess(output_bps=8)
        image = rgb
    else:
        img_bgr = cv2.imread(file_path)
        if img_bgr is None:
            raise RuntimeError("Не удалось загрузить изображение.")
        image = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    return image

def compute_indices(image):
    """
    Вычисляет набор индексов растительности на основе RGB-изображения.
    Возвращает словарь { "NDVI_emp": ..., "VARI": ..., "GLI": ..., "ExG": ..., "CIVE": ..., "MGRVI": ... }.
    """
    image = image.astype('float32')
    R = image[:, :, 0]
    G = image[:, :, 1]
    B = image[:, :, 2]
    epsilon = 1e-6
    indices = {}
    ndvi_emp = (G - R) / (G + R + epsilon)
    indices["NDVI_emp"] = ndvi_emp
    vari = (G - R) / (G + R - B + epsilon)
    indices["VARI"] = vari
    gli = (2 * G - R - B) / (2 * G + R + B + epsilon)
    indices["GLI"] = gli
    exg = 2 * G - R - B
    indices["ExG"] = exg
    cive = 0.441 * R - 0.881 * G + 0.385 * B + 18.78745
    indices["CIVE"] = cive
    mgrvi = (G**2 - R**2) / (G**2 + R**2 + epsilon)
    indices["MGRVI"] = mgrvi
    return indices

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
    norm = (index_map - idx_min) / (idx_max - idx_min + 1e-6)
    norm_uint8 = (norm * 255).astype('uint8')
    heatmap_bgr = cv2.applyColorMap(norm_uint8, cv2.COLORMAP_JET)
    heatmap_rgb = cv2.cvtColor(heatmap_bgr, cv2.COLOR_BGR2RGB)
    cv2.imwrite(output_path, heatmap_rgb)

def classify_index(index_map):
    """
    Классифицирует состояние растительности по значению индекса.
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
    main_cat = max(stats, key=stats.get)
    if main_cat == "Здоровые":
        conclusion = "Большая часть поля здорова, но встречаются участки стресса."
    elif main_cat == "Легкий стресс":
        conclusion = "Преобладает легкий стресс, возможно небольшое ухудшение состояния."
    elif main_cat == "Сильный стресс":
        conclusion = "Многие участки поля находятся в сильном стрессе. Требуются меры."
    else:
        conclusion = "Поле в критическом состоянии или отсутствует растительность."
    return stats, conclusion 