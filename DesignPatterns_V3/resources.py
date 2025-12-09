from PyQt5.QtGui import QColor

# Цветовая схема
PRIMARY_COLOR = "#2E7D32"  # Темно-зеленый
SECONDARY_COLOR = "#4CAF50"  # Зеленый
BACKGROUND_COLOR = "#FFFFFF"  # Белый
TEXT_COLOR = "#333333"  # Темно-серый

# Стили для кнопок
BUTTON_STYLE = """
QPushButton {
    background-color: """ + PRIMARY_COLOR + """;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 6px;
    font-size: 16px;
    min-width: 200px;
}
QPushButton:hover {
    background-color: """ + SECONDARY_COLOR + """;
}
QPushButton:disabled {
    background-color: #CCCCCC;
}
"""

# Стили для меню
MENU_STYLE = """
QMenuBar {
    background-color: """ + PRIMARY_COLOR + """;
    color: white;
    font-size: 16px;
    padding: 8px;
}
QMenuBar::item:selected {
    background-color: """ + SECONDARY_COLOR + """;
}
QMenu {
    background-color: white;
    color: """ + TEXT_COLOR + """;
    font-size: 14px;
    padding: 8px;
}
QMenu::item:selected {
    background-color: """ + SECONDARY_COLOR + """;
    color: white;
}
"""

# Стили для главного окна
MAIN_WINDOW_STYLE = """
QMainWindow {
    background-color: """ + BACKGROUND_COLOR + """;
}
QLabel {
    color: """ + TEXT_COLOR + """;
    font-size: 14px;
}
QTextEdit {
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    padding: 8px;
    font-size: 14px;
    background-color: white;
}
QComboBox {
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    padding: 8px;
    min-width: 200px;
    font-size: 14px;
    background-color: white;
}
QSpinBox, QDoubleSpinBox {
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    padding: 8px;
    min-width: 100px;
    font-size: 14px;
    background-color: white;
}
QCheckBox {
    font-size: 14px;
    spacing: 8px;
}
QGroupBox {
    font-size: 14px;
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    margin-top: 16px;
    padding-top: 16px;
    background-color: white;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px;
}
QDialog {
    background-color: white;
}
QMessageBox {
    background-color: white;
}
QStatusBar {
    background-color: """ + PRIMARY_COLOR + """;
    color: white;
    font-size: 14px;
    padding: 4px;
}
"""

# Пороговые значения для разных культур
CROP_THRESHOLDS = {
    "Кукуруза": {
        "healthy": 0.7,
        "stressed": 0.4,
        "description": "Кукуруза требует высокого значения NDVI для здорового роста"
    },
    "Пшеница": {
        "healthy": 0.65,
        "stressed": 0.35,
        "description": "Пшеница имеет средние требования к NDVI"
    },
    "Ячмень": {
        "healthy": 0.6,
        "stressed": 0.3,
        "description": "Ячмень может расти при более низких значениях NDVI"
    }
}

# Описания спектральных индексов
SPECTRAL_INDEX_DESCRIPTIONS = {
    "NDVI": {
        "name": "Нормализованный разностный вегетационный индекс (NDVI)",
        "description": "Показывает относительное количество здоровой растительности. Значения от -1 до 1, где:\n- Высокие значения (>0.6) указывают на здоровую растительность\n- Средние значения (0.2-0.6) указывают на умеренный стресс\n- Низкие значения (<0.2) указывают на сильный стресс или отсутствие растительности",
        "formula": "(NIR - Red) / (NIR + Red)"
    },
    "Civi": {
        "name": "Цветовой индекс вегетации (Civi)",
        "description": "Индекс, основанный на цветовых характеристиках растительности. Полезен для оценки общего состояния растений и определения областей с потенциальными проблемами.",
        "formula": "((NIR - Red) / (NIR + Red)) * (NIR / Red)"
    },
    "exG": {
        "name": "Избыточный зеленый индекс (ExG)",
        "description": "Индекс, который подчеркивает зеленую растительность и подавляет почву и тени. Эффективен для сегментации растительности.",
        "formula": "2 * Green - Red - Blue"
    },
    "MGRVI": {
        "name": "Модифицированный индекс зеленой растительности (MGRVI)",
        "description": "Улучшенная версия NDVI, которая лучше работает в условиях высокой плотности растительности и при различных условиях освещения.",
        "formula": "(Green^2 - Red^2) / (Green^2 + Red^2)"
    }
}

# Переводы
TRANSLATIONS = {
    "Русский": {
        "app_title": "Мониторинг состояния полей",
        "start_analysis": "Начать анализ",
        "settings": "Настройки",
        "about": "О программе",
        "load_image": "Загрузить изображение",
        "analyze": "Анализировать",
        "save_report": "Сохранить отчет (PDF)",
        "original_image": "Исходное изображение",
        "heatmap": "Тепловая карта",
        "language": "Язык",
        "threshold": "Пороговое значение NDVI",
        "stress_threshold": "Порог стресса",
        "vegetation_threshold": "Порог растительности",
        "crop_type": "Тип культуры",
        "auto_boundaries": "Автоматическое определение границ",
        "enhance_contrast": "Усиление контраста",
        "current_formula": "Текущая формула: (NIR - Red) / (NIR + Red)",
        "multispectral_camera": "Использовать мультиспектральную камеру",
        "threshold_note": "Примечание: Пороговые значения NDVI используются для определения состояния растений. Значения выше порога растительности указывают на здоровые растения, значения ниже порога стресса - на проблемные участки.",
        "about_text": """
        <h2>Мониторинг состояния полей</h2>
        <p>Версия 2.0</p>
        <p>Приложение для анализа состояния сельскохозяйственных культур по аэрофотоснимкам.</p>
        <h3>Как использовать:</h3>
        <ol>
            <li>Выберите тип культуры в настройках</li>
            <li>Настройте пороговые значения NDVI при необходимости</li>
            <li>Загрузите аэрофотоснимок через кнопку \"Загрузить изображение\"</li>
            <li>Нажмите \"Анализировать\" для обработки изображения</li>
            <li>Просмотрите результаты анализа и тепловую карту</li>
            <li>При необходимости сохраните отчет в PDF</li>
        </ol>
        <h3>Возможности:</h3>
        <ul>
            <li>Анализ NDVI и других вегетационных индексов</li>
            <li>Генерация тепловых карт</li>
            <li>Классификация состояния растений</li>
            <li>Настройка пороговых значений для разных культур</li>
            <li>Автоматическое определение границ полей</li>
        </ul>
        """,
        "back_to_menu": "Вернуться в главное меню",
        "export_success": "Отчет успешно сохранен!",
        "export_error": "Ошибка при сохранении отчета: {}"
    },
    "Română": {
        "app_title": "Monitorizarea stării terenurilor",
        "start_analysis": "Începe analiza",
        "settings": "Setări",
        "about": "Despre program",
        "load_image": "Încărcați imaginea",
        "analyze": "Analiza",
        "save_report": "Salvați raportul (PDF)",
        "original_image": "Imagine originală",
        "heatmap": "Hartă termică",
        "language": "Limbă",
        "threshold": "Valoarea pragului NDVI",
        "stress_threshold": "Pragul stresului",
        "vegetation_threshold": "Pragul vegetației",
        "crop_type": "Tipul culturii",
        "auto_boundaries": "Determinarea automată a frontierelor",
        "enhance_contrast": "Îmbunătățirea contrastului",
        "current_formula": "Formula curentă: (NIR - Red) / (NIR + Red)",
        "multispectral_camera": "Utilizați camera multispectrală",
        "threshold_note": "Notă: Valorile pragului NDVI sunt utilizate pentru determinarea stării plantelor. Valorile peste pragul vegetației indică plante sănătoase, valorile sub pragul stresului indică zonele cu probleme",
        "about_text": """
        <h2>Monitorizarea stării terenurilor</h2>
        <p>Versiunea 2.0</p>
        <p>Aplicatia pentru analiza stării culturilor agricole pe baza fotografiilor aeriene.</p>
        <h3>Cum să o folosești:</h3>
        <ol>
            <li>Selectați tipul culturii în setări</li>
            <li>Ajustați valorile pragurilor NDVI atunci când este necesar</li>
            <li>Încărcați fotografia aeriană prin butonul \"Încărcați imaginea\"</li>
            <li>Apăsați \"Analiza\" pentru procesarea imaginii</li>
            <li>Vizualizați rezultatele analizei și harta termică</li>
            <li>Salvați raportul în PDF atunci când este necesar</li>
        </ol>
        <h3>Funcționalități:</h3>
        <ul>
            <li>Analiza NDVI și a altor indici vegetaționali</li>
            <li>Generarea hărților termice</li>
            <li>Clasificarea stării plantelor</li>
            <li>Ajustarea valorilor pragurilor pentru diferite culturi</li>
            <li>Determinarea automată a frontierelor terenurilor</li>
        </ul>
        """,
        "back_to_menu": "Înapoi la meniul principal",
        "export_success": "Raportul a fost salvat cu succes!",
        "export_error": "Eroare la salvarea raportului: {}"
    }
} 