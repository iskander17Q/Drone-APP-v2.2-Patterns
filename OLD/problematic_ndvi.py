import os
import cv2
import numpy as np
from analysis import load_image

def generate_problematic_ndvi_image(input_image_path, output_path, threshold=0.1, overlay_color=(0,0,255), alpha=0.5):
    """
    Генерирует изображение на основе приближённого NDVI, в котором проблемные области выделены красным цветом.
    
    Параметры:
      input_image_path - путь к исходному изображению
      output_path - путь для сохранения итогового изображения
      threshold - порог NDVI, ниже которого участок считается проблемным (по умолчанию 0.1)
      overlay_color - цвет для наложения (BGR, по умолчанию красный: (0, 0, 255))
      alpha - коэффициент прозрачности наложения (0..1, по умолчанию 0.5)
    """
    # Загружаем исходное изображение (в формате RGB)
    image_rgb = load_image(input_image_path)
    image_rgb = image_rgb.astype('float32')
    
    # Разбиваем на каналы
    R = image_rgb[:, :, 0]
    G = image_rgb[:, :, 1]
    B = image_rgb[:, :, 2]
    epsilon = 1e-6
    # Вычисляем приближённый NDVI (используем G вместо NIR)
    ndvi = (G - R) / (G + R + epsilon)
    
    # Создаем маску проблемных участков: NDVI ниже порога
    problematic_mask = ndvi < threshold  # проблемные области
    
    # Преобразуем исходное изображение в BGR для наложения (OpenCV работает с BGR)
    image_bgr = cv2.cvtColor(image_rgb.astype('uint8'), cv2.COLOR_RGB2BGR)
    
    # Создаем копию для наложения
    overlay = image_bgr.copy()
    # Накладываем заданный цвет на проблемные области
    overlay[problematic_mask] = overlay_color
    
    # Смешиваем оригинальное изображение и оверлей
    output_image = cv2.addWeighted(overlay, alpha, image_bgr, 1 - alpha, 0)
    
    # Сохраняем итоговое изображение
    cv2.imwrite(output_path, output_image)
    print(f"Изображение с выделенными проблемными участками сохранено в: {output_path}")

# Пример использования: если запускать этот файл напрямую, можно передать аргументы.
if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("Использование: python problematic_ndvi.py input_image_path output_image_path [threshold]")
    else:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
        thresh = float(sys.argv[3]) if len(sys.argv) > 3 else 0.1
        generate_problematic_ndvi_image(input_path, output_path, threshold=thresh)