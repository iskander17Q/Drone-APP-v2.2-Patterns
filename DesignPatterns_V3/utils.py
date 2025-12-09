import os
from datetime import datetime

from PIL import Image, ExifTags
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from patterns.adapter import GPSData, GpsMetadataAdapter
from patterns.report_builder import ReportBuilder, ReportDirector, ReportPayload

def get_gps_from_image(file_path):
    """
    Извлекает GPS-данные из EXIF метаданных изображения.
    Возвращает словарь с ключами 'latitude' и 'longitude', либо None, если данные отсутствуют.
    """
    try:
        image = Image.open(file_path)
        exif_data = image._getexif()
        if exif_data is None:
            return None
        # Формируем словарь EXIF-данных с читаемыми тегами
        exif = {}
        for k, v in exif_data.items():
            if k in ExifTags.TAGS:
                exif[ExifTags.TAGS[k]] = v
        if "GPSInfo" not in exif:
            return None
        gps_info = exif["GPSInfo"]
        gps_data = GpsMetadataAdapter.convert(gps_info)
        if gps_data.is_valid():
            return gps_data.to_dict()
        return None
    except Exception as e:
        # Если возникает ошибка, можно записать её в лог
        return None

def generate_pdf_report(pdf_path, original_image_path, heatmap_image_path, report_text, gps, index_type="NDVI_emp"):
    """
    Генерирует PDF-отчет, содержащий:
      - Заголовок и дату анализа
      - Исходное изображение и тепловую карту
      - Текстовый отчет с результатами анализа
      - GPS данные (если имеются)
    
    Используется шрифт DejaVuSans, поддерживающий кириллицу.
    """
    # Определяем путь к шрифту DejaVuSans. Убедитесь, что файл 'DejaVuSans.ttf' находится в этой же директории.
    font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")
    try:
        pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
    except Exception as e:
        # Если регистрация шрифта не удалась, выводим сообщение в консоль
        print("Не удалось зарегистрировать шрифт DejaVuSans. Проверьте наличие файла:", font_path)
    
    def gps_to_text(data) -> str:
        if isinstance(data, GPSData):
            return data.to_display()
        if data and data.get("latitude") is not None and data.get("longitude") is not None:
            return f"GPS данные: Широта {data.get('latitude')}, Долгота {data.get('longitude')}"
        return "GPS данные: не обнаружены"

    payload = ReportPayload(
        pdf_path=pdf_path,
        original_image_path=original_image_path,
        heatmap_image_path=heatmap_image_path,
        report_text=report_text,
        gps_text=gps_to_text(gps),
        index_type=index_type,
    )
    builder = ReportBuilder(payload)
    director = ReportDirector(builder)
    director.build()
