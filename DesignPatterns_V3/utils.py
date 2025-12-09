import os
from PIL import Image, ExifTags
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

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
        
        def convert_to_degrees(value):
            d = value[0][0] / value[0][1]
            m = value[1][0] / value[1][1]
            s = value[2][0] / value[2][1]
            return d + (m / 60.0) + (s / 3600.0)
        
        lat = convert_to_degrees(gps_info[2]) if 2 in gps_info else None
        lon = convert_to_degrees(gps_info[4]) if 4 in gps_info else None
        
        lat_ref = gps_info[1] if 1 in gps_info else "N"
        lon_ref = gps_info[3] if 3 in gps_info else "E"
        if lat and lat_ref.upper() != "N":
            lat = -lat
        if lon and lon_ref.upper() != "E":
            lon = -lon
        return {"latitude": lat, "longitude": lon}
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
    
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4  # Размер страницы A4 (595 x 842 точек)
    
    # Заголовок и дата анализа
    c.setFont("DejaVuSans", 20)
    c.drawCentredString(width / 2, height - 50, "Отчет по анализу состояния поля")
    
    c.setFont("DejaVuSans", 12)
    current_date = datetime.now().strftime("%d.%m.%Y %H:%M")
    c.drawCentredString(width / 2, height - 70, f"Дата анализа: {current_date}")
    
    # Вставка исходного изображения
    try:
        c.drawImage(original_image_path, 50, height - 350, width=250, height=250, preserveAspectRatio=True)
        c.drawString(50, height - 360, "Исходное изображение")
    except Exception as e:
        c.drawString(50, height - 350, "Не удалось загрузить исходное изображение.")
    
    # Вставка тепловой карты
    try:
        c.drawImage(heatmap_image_path, 320, height - 350, width=250, height=250, preserveAspectRatio=True)
        c.drawString(320, height - 360, f"Тепловая карта ({index_type})")
    except Exception as e:
        c.drawString(320, height - 350, "Не удалось загрузить тепловую карту.")
    
    # Текстовый отчет
    text_obj = c.beginText()
    text_obj.setTextOrigin(50, height - 370)
    text_obj.setFont("DejaVuSans", 12)
    for line in report_text.splitlines():
        text_obj.textLine(line)
    c.drawText(text_obj)
    
    # Вывод GPS-данных (если имеются)
    if gps:
        gps_text = f"GPS данные: Широта {gps.get('latitude', 'N/A')}, Долгота {gps.get('longitude', 'N/A')}"
    else:
        gps_text = "GPS данные: не обнаружены"
    c.drawString(50, 50, gps_text)
    
    c.showPage()
    c.save()