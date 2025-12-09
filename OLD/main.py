import sys
import os
import cv2
import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
import datetime
from PyQt5.QtGui import QIcon, QPixmap

# Импортируем функции анализа из analysis.py
from analysis import load_image, compute_indices, generate_heatmap, classify_index
from utils import get_gps_from_image, generate_pdf_report
from styles import (BUTTON_STYLE, MENU_STYLE, MAIN_WINDOW_STYLE, 
                   CROP_THRESHOLDS, TRANSLATIONS, SPECTRAL_INDEX_DESCRIPTIONS)

# Импорт ресурсов и функций
from resources import BUTTON_STYLE, MENU_STYLE, MAIN_WINDOW_STYLE, CROP_THRESHOLDS, TRANSLATIONS, SPECTRAL_INDEX_DESCRIPTIONS
from image_processing import load_image, compute_indices, generate_heatmap, classify_index

class MainMenu(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(20)

        # Абсолютный слой для выбора языка (только текст)
        lang_widget = QtWidgets.QWidget(self)
        lang_layout = QtWidgets.QHBoxLayout()
        lang_layout.setContentsMargins(0, 0, 10, 0)
        lang_layout.addStretch()
        self.lang_combo = QtWidgets.QComboBox()
        self.lang_combo.addItem("Русский")
        self.lang_combo.addItem("Română")
        self.lang_combo.setCurrentIndex(0)
        self.lang_combo.setMinimumWidth(160)
        self.lang_combo.setMaximumWidth(180)
        self.lang_combo.setStyleSheet("background: white; color: #222; border: 2px solid #2E7D32; border-radius: 6px; font-size: 15px; padding: 4px 12px;")
        self.lang_combo.setToolTip("Выберите язык интерфейса / Select language")
        lang_layout.addWidget(self.lang_combo)
        lang_widget.setLayout(lang_layout)
        lang_widget.setFixedHeight(40)
        lang_widget.setFixedWidth(170)
        lang_widget.move(self.width() - 180, 20)
        lang_widget.setStyleSheet("background: transparent;")
        lang_widget.raise_()
        self.lang_widget = lang_widget

        # Заголовок
        self.title = QtWidgets.QLabel(TRANSLATIONS["Русский"]["app_title"])
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2E7D32;")
        self.title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.title)

        # Кнопки главного меню
        self.btn_start = QtWidgets.QPushButton(TRANSLATIONS["Русский"]["start_analysis"])
        self.btn_start.setToolTip("Начать анализ — загрузите снимок и получите результат")
        self.btn_settings = QtWidgets.QPushButton(TRANSLATIONS["Русский"]["settings"])
        self.btn_settings.setToolTip("Настройки анализа и отображения")
        self.btn_about = QtWidgets.QPushButton(TRANSLATIONS["Русский"]["about"])
        self.btn_about.setToolTip("Информация о приложении и инструкции")

        for btn in [self.btn_start, self.btn_settings, self.btn_about]:
            btn.setStyleSheet(BUTTON_STYLE)
            main_layout.addWidget(btn)

        self.setLayout(main_layout)

    def resizeEvent(self, event):
        self.lang_widget.move(self.width() - self.lang_widget.width() - 40, 20)
        super().resizeEvent(event)

    def update_language(self, lang):
        self.title.setText(TRANSLATIONS[lang]["app_title"])
        self.btn_start.setText(TRANSLATIONS[lang]["start_analysis"])
        self.btn_settings.setText(TRANSLATIONS[lang]["settings"])
        self.btn_about.setText(TRANSLATIONS[lang]["about"])

    def showEvent(self, event):
        super().showEvent(event)
        self.lang_combo.setMinimumWidth(160)
        self.lang_combo.setMaximumWidth(180)
        self.lang_combo.updateGeometry()

class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        self.setWindowTitle(TRANSLATIONS["Русский"]["settings"])
        self.setModal(True)
        self.current_settings = current_settings or {}
        self.setup_ui()
        self.setMinimumSize(500, 600)
        self.center_on_screen()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout()
        self.setStyleSheet("QLabel, QCheckBox { color: #222; } QGroupBox { color: #222; } QDoubleSpinBox { color: #222; } QComboBox { color: #222; background: white; selection-background-color: #E8F5E9; selection-color: #222; border: 1.5px solid #2E7D32; } QPushButton#backBtn { background: white; color: #2E7D32; border: 2px solid #2E7D32; border-radius: 6px; font-size: 14px; padding: 6px 18px; } QPushButton#okBtn { background: #2E7D32; color: white; border: none; border-radius: 6px; font-size: 14px; padding: 8px 28px; }")
        
        # Группа настроек культуры
        crop_group = QtWidgets.QGroupBox(TRANSLATIONS["Русский"]["crop_type"])
        crop_layout = QtWidgets.QVBoxLayout()
        
        self.crop_combo = QtWidgets.QComboBox()
        self.crop_combo.addItems(CROP_THRESHOLDS.keys())
        crop_layout.addWidget(self.crop_combo)
        
        self.crop_description = QtWidgets.QLabel()
        self.crop_description.setWordWrap(True)
        crop_layout.addWidget(self.crop_description)
        
        crop_group.setLayout(crop_layout)
        layout.addWidget(crop_group)
        
        # Группа пороговых значений
        threshold_group = QtWidgets.QGroupBox(TRANSLATIONS["Русский"]["threshold"])
        threshold_layout = QtWidgets.QVBoxLayout()
        
        # Порог стресса
        stress_layout = QtWidgets.QHBoxLayout()
        stress_label = QtWidgets.QLabel(TRANSLATIONS["Русский"]["stress_threshold"])
        self.stress_input = QtWidgets.QDoubleSpinBox()
        self.stress_input.setRange(0.0, 1.0)
        self.stress_input.setSingleStep(0.05)
        stress_layout.addWidget(stress_label)
        stress_layout.addWidget(self.stress_input)
        threshold_layout.addLayout(stress_layout)
        
        # Порог растительности
        veg_layout = QtWidgets.QHBoxLayout()
        veg_label = QtWidgets.QLabel(TRANSLATIONS["Русский"]["vegetation_threshold"])
        self.veg_input = QtWidgets.QDoubleSpinBox()
        self.veg_input.setRange(0.0, 1.0)
        self.veg_input.setSingleStep(0.05)
        veg_layout.addWidget(veg_label)
        veg_layout.addWidget(self.veg_input)
        threshold_layout.addLayout(veg_layout)
        
        # Примечание
        note_label = QtWidgets.QLabel(TRANSLATIONS["Русский"]["threshold_note"])
        note_label.setWordWrap(True)
        note_label.setStyleSheet("font-size: 11px; color: #444;")
        threshold_layout.addWidget(note_label)
        
        threshold_group.setLayout(threshold_layout)
        layout.addWidget(threshold_group)
        
        # Группа дополнительных настроек
        advanced_group = QtWidgets.QGroupBox(TRANSLATIONS["Русский"]["settings"])
        advanced_layout = QtWidgets.QVBoxLayout()
        self.auto_boundaries = QtWidgets.QCheckBox(TRANSLATIONS["Русский"]["auto_boundaries"])
        advanced_layout.addWidget(self.auto_boundaries)
        self.enhance_contrast = QtWidgets.QCheckBox(TRANSLATIONS["Русский"]["enhance_contrast"])
        advanced_layout.addWidget(self.enhance_contrast)
        # Мультиспектральная камера
        self.multispectral = QtWidgets.QCheckBox(TRANSLATIONS["Русский"]["multispectral_camera"])
        advanced_layout.addWidget(self.multispectral)
        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)
        # Кнопки (меняем местами)
        btns_layout = QtWidgets.QHBoxLayout()
        self.btn_back = QtWidgets.QPushButton("Назад")
        self.btn_back.setObjectName("backBtn")
        self.btn_back.clicked.connect(self.reject)
        btns_layout.addWidget(self.btn_back)
        self.btn_ok = QtWidgets.QPushButton("Окей")
        self.btn_ok.setObjectName("okBtn")
        self.btn_ok.clicked.connect(self.accept)
        btns_layout.addWidget(self.btn_ok)
        layout.addLayout(btns_layout)
        self.setLayout(layout)
        # Устанавливаем значения из current_settings
        crop = self.current_settings.get("crop", list(CROP_THRESHOLDS.keys())[0])
        self.crop_combo.setCurrentText(crop)
        self.update_thresholds(crop)
        self.stress_input.setValue(self.current_settings.get("stress", CROP_THRESHOLDS[crop]["stressed"]))
        self.veg_input.setValue(self.current_settings.get("veg", CROP_THRESHOLDS[crop]["healthy"]))
        self.auto_boundaries.setChecked(self.current_settings.get("auto_boundaries", False))
        self.enhance_contrast.setChecked(self.current_settings.get("enhance_contrast", False))
        self.multispectral.setChecked(self.current_settings.get("multispectral", False))
        self.crop_combo.currentTextChanged.connect(self.update_thresholds)

    def update_thresholds(self, crop_type):
        if crop_type in CROP_THRESHOLDS:
            thresholds = CROP_THRESHOLDS[crop_type]
            self.stress_input.setValue(thresholds["stressed"])
            self.veg_input.setValue(thresholds["healthy"])
            self.crop_description.setText(thresholds["description"])

    def get_settings(self):
        return {
            "crop": self.crop_combo.currentText(),
            "stress": self.stress_input.value(),
            "veg": self.veg_input.value(),
            "auto_boundaries": self.auto_boundaries.isChecked(),
            "enhance_contrast": self.enhance_contrast.isChecked(),
            "multispectral": self.multispectral.isChecked()
        }

    def center_on_screen(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

class AboutDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(TRANSLATIONS["Русский"]["about"])
        self.setModal(True)
        self.setup_ui()
        self.setMinimumSize(800, 600)
        self.center_on_screen()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout()
        text_edit = QtWidgets.QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setHtml(TRANSLATIONS["Русский"]["about_text"])
        text_edit.setStyleSheet("color: #222; background: white; font-size: 15px;")
        layout.addWidget(text_edit)
        close_button = QtWidgets.QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)
        close_button.setStyleSheet(BUTTON_STYLE)
        layout.addWidget(close_button)
        self.setLayout(layout)

    def center_on_screen(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

class AnalysisWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.current_image_path = None
        self.current_heatmap_path = None
        self.current_stats = None
        self.current_gps = None

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout()
        
        # Панель кнопок (верхняя)
        button_layout = QtWidgets.QHBoxLayout()
        
        # Добавляем кнопку возврата в главное меню
        self.btn_back = QtWidgets.QPushButton(TRANSLATIONS["Русский"]["back_to_menu"])
        self.btn_back.clicked.connect(self.back_to_menu)
        button_layout.addWidget(self.btn_back)
        
        self.btn_load = QtWidgets.QPushButton(TRANSLATIONS["Русский"]["load_image"])
        self.btn_load.clicked.connect(self.load_image_file)
        button_layout.addWidget(self.btn_load)
        
        self.btn_analyze = QtWidgets.QPushButton(TRANSLATIONS["Русский"]["analyze"])
        self.btn_analyze.clicked.connect(self.analyze_image)
        self.btn_analyze.setEnabled(False)
        button_layout.addWidget(self.btn_analyze)
        
        self.btn_save = QtWidgets.QPushButton(TRANSLATIONS["Русский"]["save_report"])
        self.btn_save.clicked.connect(self.save_report)
        self.btn_save.setEnabled(False)
        button_layout.addWidget(self.btn_save)
        
        layout.addLayout(button_layout)
        
        # Отображение изображений
        images_layout = QtWidgets.QHBoxLayout()
        
        # Исходное изображение
        original_layout = QtWidgets.QVBoxLayout()
        self.label_original = QtWidgets.QLabel(TRANSLATIONS["Русский"]["original_image"])
        self.label_original.setAlignment(QtCore.Qt.AlignCenter)
        self.label_original.setFixedHeight(400)
        self.label_original.setStyleSheet("border: 1px solid #CCCCCC; border-radius: 4px;")
        original_layout.addWidget(self.label_original)
        images_layout.addLayout(original_layout)
        
        # Тепловая карта
        heatmap_layout = QtWidgets.QVBoxLayout()
        self.label_heatmap = QtWidgets.QLabel(TRANSLATIONS["Русский"]["heatmap"])
        self.label_heatmap.setAlignment(QtCore.Qt.AlignCenter)
        self.label_heatmap.setFixedHeight(400)
        self.label_heatmap.setStyleSheet("border: 1px solid #CCCCCC; border-radius: 4px;")
        heatmap_layout.addWidget(self.label_heatmap)
        images_layout.addLayout(heatmap_layout)
        
        layout.addLayout(images_layout)
        
        # Текстовый отчет
        self.text_report = QtWidgets.QTextEdit()
        self.text_report.setReadOnly(True)
        self.text_report.setFixedHeight(200)
        self.text_report.setStyleSheet("background: white; color: #222; font-size: 15px;")
        layout.addWidget(self.text_report)
        
        self.setLayout(layout)

    def load_image_file(self):
        """Загрузка файла изображения с диска."""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Выбрать изображение",
            "",
            "Изображения (*.jpg *.jpeg *.png *.bmp *.raw *.dng *.nef *.cr2 *.arw)"
        )
        if file_path:
            self.current_image_path = file_path
            # Отображаем исходное изображение в label
            pixmap = QtGui.QPixmap(file_path)
            if not pixmap.isNull():
                if (pixmap.width() > self.label_original.width() or 
                    pixmap.height() > self.label_original.height()):
                    pixmap = pixmap.scaled(self.label_original.size(), 
                                           QtCore.Qt.KeepAspectRatio,
                                           QtCore.Qt.SmoothTransformation)
                self.label_original.setPixmap(pixmap)
            else:
                self.label_original.setText("Не удалось отобразить изображение.")
            
            self.label_heatmap.clear()
            self.text_report.clear()
            
            self.btn_analyze.setEnabled(True)
            # Попытка извлечь GPS-данные
            self.current_gps = get_gps_from_image(file_path)
            if self.current_gps:
                gps_text = f"GPS: {self.current_gps.get('latitude', 'N/A')}, {self.current_gps.get('longitude', 'N/A')}"
            else:
                gps_text = "GPS: не обнаружены"
            # Исправляем отображение GPS-информации
            main_window = self.window()
            if isinstance(main_window, QtWidgets.QMainWindow):
                main_window.statusBar().showMessage(gps_text)

    def analyze_image(self):
        """Запускает анализ индексов и отображает тепловую карту."""
        if not self.current_image_path:
            return
        
        try:
            # Загружаем изображение и считаем индексы
            image = load_image(self.current_image_path)
            indices = compute_indices(image)
            
            # Используем один из индексов для отображения тепловой карты
            index_map = indices.get("NDVI_emp")
            if index_map is None:
                index_map = list(indices.values())[0]
            
            # Генерируем тепловую карту (в папке assets)
            os.makedirs("assets", exist_ok=True)
            heatmap_filename = os.path.join("assets", "heatmap_temp.png")
            generate_heatmap(index_map, heatmap_filename)
            self.current_heatmap_path = heatmap_filename
            
            # Отображаем тепловую карту в label
            pixmap = QtGui.QPixmap(heatmap_filename)
            if not pixmap.isNull():
                if (pixmap.width() > self.label_heatmap.width() or 
                    pixmap.height() > self.label_heatmap.height()):
                    pixmap = pixmap.scaled(self.label_heatmap.size(),
                                           QtCore.Qt.KeepAspectRatio,
                                           QtCore.Qt.SmoothTransformation)
                self.label_heatmap.setPixmap(pixmap)
            else:
                self.label_heatmap.setText("Не удалось отобразить тепловую карту.")
            
            # Классифицируем состояние поля
            stats, conclusion = classify_index(index_map)
            self.current_stats = stats  # сохраняем, если нужно
            
            # Формируем текст отчёта
            report_text = "Распределение состояния растений:\n"
            for category, pct in stats.items():
                report_text += f"{category}: {pct:.1f}%\n"
            report_text += "\nВывод: " + conclusion
            self.text_report.setText(report_text)
            
            # Активируем кнопку сохранения PDF
            self.btn_save.setEnabled(True)
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка при анализе: {str(e)}")

    def back_to_menu(self):
        """Возврат в главное меню."""
        self.hide()
        main_window = self.window()
        if isinstance(main_window, QtWidgets.QMainWindow):
            main_window.main_menu.show()

    def save_report(self):
        """Сохраняет PDF-отчет и экспортирует все спектральные карты в подпапку рядом с PDF."""
        if not self.current_image_path or not self.current_heatmap_path:
            return
        pdf_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            TRANSLATIONS[self.window().current_language]["save_report"],
            "",
            "PDF Files (*.pdf)"
        )
        if pdf_path:
            try:
                generate_pdf_report(
                    pdf_path,
                    self.current_image_path,
                    self.current_heatmap_path,
                    self.text_report.toPlainText(),
                    self.current_gps,
                    index_type="NDVI_emp"
                )
                # Экспорт спектральных карт в подпапку рядом с PDF
                import os
                from image_processing import load_image, compute_indices, generate_heatmap
                from resources import SPECTRAL_INDEX_DESCRIPTIONS
                image = load_image(self.current_image_path)
                indices = compute_indices(image)
                export_dir = os.path.splitext(pdf_path)[0] + "_spectral_maps"
                os.makedirs(export_dir, exist_ok=True)
                readme_lines = ["СПЕКТРАЛЬНЫЕ КАРТЫ:\n"]
                for index_name, index_map in indices.items():
                    output_path = os.path.join(export_dir, f"{index_name}.png")
                    generate_heatmap(index_map, output_path)
                    desc_key = index_name.lower().replace('_emp','').replace('cive','civi').replace('exg','exg').replace('mgrvi','mgrvi').replace('ndvi','ndvi')
                    desc = None
                    for k in SPECTRAL_INDEX_DESCRIPTIONS:
                        if k.lower() == desc_key:
                            desc = SPECTRAL_INDEX_DESCRIPTIONS[k]
                            break
                    import matplotlib.pyplot as plt
                    plt.figure(figsize=(10, 6))
                    plt.imshow(index_map, cmap='RdYlGn')
                    plt.title(desc["name"] if desc else index_name)
                    plt.colorbar(label='Значение индекса')
                    plt.axis('off')
                    # Только описание, без формулы и 'Без описания'
                    if desc and desc.get('description'):
                        description = f"{desc['name']}\n\n{desc['description']}"
                        plt.figtext(0.5, 0.01, description, wrap=True, fontsize=9, ha='center', va='bottom', bbox={'facecolor':'white', 'alpha':0.7, 'pad':6})
                    desc_path = os.path.join(export_dir, f"{index_name}_desc.png")
                    plt.savefig(desc_path, bbox_inches='tight', dpi=200)
                    plt.close()
                    # В README только название и описание, без формулы и 'Без описания'
                    if desc and desc.get('description'):
                        readme_lines.append(f"{index_name}: {desc['name']}\n{desc['description']}\n")
                    else:
                        readme_lines.append(f"{index_name}\n")
                readme_lines.append("\nКаждый PNG-файл — это визуализация определённого индекса. Файл *_desc.png содержит ту же карту с кратким описанием.\nЕсли у вас возникли вопросы — обратитесь в поддержку приложения.")
                with open(os.path.join(export_dir, "README.txt"), "w", encoding="utf-8") as f:
                    f.write("\n".join(readme_lines))
                QtWidgets.QMessageBox.information(
                    self,
                    "Успех",
                    TRANSLATIONS[self.window().current_language]["export_success"] + f"\nПапка с анализами: {export_dir}"
                )
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Ошибка",
                    TRANSLATIONS[self.window().current_language]["export_error"].format(str(e))
                )

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_language = "Русский"
        self.user_settings = {
            "crop": list(CROP_THRESHOLDS.keys())[0],
            "stress": CROP_THRESHOLDS[list(CROP_THRESHOLDS.keys())[0]]["stressed"],
            "veg": CROP_THRESHOLDS[list(CROP_THRESHOLDS.keys())[0]]["healthy"],
            "auto_boundaries": False,
            "enhance_contrast": False,
            "multispectral": False
        }
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        self.setWindowTitle(TRANSLATIONS[self.current_language]["app_title"])
        self.setGeometry(100, 100, 1200, 800)
        
        # Центральный виджет и основной layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Главное меню
        self.main_menu = MainMenu()
        main_layout.addWidget(self.main_menu)
        
        # Окно анализа (изначально скрыто)
        self.analysis_window = AnalysisWindow(self)
        self.analysis_window.hide()
        main_layout.addWidget(self.analysis_window)
        
        # Подключаем сигналы кнопок главного меню
        self.main_menu.btn_start.clicked.connect(self.show_analysis)
        self.main_menu.btn_settings.clicked.connect(self.show_settings)
        self.main_menu.btn_about.clicked.connect(self.show_about)
        # Подключаем сигнал выбора языка
        self.main_menu.lang_combo.currentIndexChanged.connect(self.on_language_combo_changed)
        
        # Создаём меню
        self.create_menus()
        
        # Добавляем строку состояния
        self.statusBar().showMessage("")

    def create_menus(self):
        menu_bar = self.menuBar()
        
        # Меню "Файл"
        file_menu = menu_bar.addMenu("Файл")
        
        action_save_pdf = QtWidgets.QAction(TRANSLATIONS[self.current_language]["save_report"], self)
        action_save_pdf.triggered.connect(self.analysis_window.save_report)
        file_menu.addAction(action_save_pdf)
        
        # Меню "Настройки"
        settings_menu = menu_bar.addMenu(TRANSLATIONS[self.current_language]["settings"])
        
        action_settings = QtWidgets.QAction(TRANSLATIONS[self.current_language]["settings"], self)
        action_settings.triggered.connect(self.show_settings)
        settings_menu.addAction(action_settings)
        
        # Подменю выбора языка (в правом верхнем углу)
        language_menu = menu_bar.addMenu(TRANSLATIONS[self.current_language]["language"])
        language_menu.setStyleSheet("""
            QMenu {
                position: absolute;
                right: 0;
            }
        """)
        
        action_russian = QtWidgets.QAction("Русский", self)
        action_russian.triggered.connect(lambda: self.change_language("Русский"))
        language_menu.addAction(action_russian)
        
        action_romanian = QtWidgets.QAction("Română", self)
        action_romanian.triggered.connect(lambda: self.change_language("Română"))
        language_menu.addAction(action_romanian)
        
        # Меню "О программе"
        about_menu = menu_bar.addMenu(TRANSLATIONS[self.current_language]["about"])
        
        action_about = QtWidgets.QAction(TRANSLATIONS[self.current_language]["about"], self)
        action_about.triggered.connect(self.show_about)
        about_menu.addAction(action_about)

    def apply_styles(self):
        self.setStyleSheet(MAIN_WINDOW_STYLE)
        self.menuBar().setStyleSheet(MENU_STYLE)
        
        for button in self.findChildren(QtWidgets.QPushButton):
            button.setStyleSheet(BUTTON_STYLE)

    def change_language(self, language):
        self.current_language = language
        self.setWindowTitle(TRANSLATIONS[language]["app_title"])
        self.main_menu.update_language(language)
        self.create_menus()
        idx = 0 if language == "Русский" else 1
        self.main_menu.lang_combo.setCurrentIndex(idx)

    def show_settings(self):
        dialog = SettingsDialog(self, current_settings=self.user_settings)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.user_settings = dialog.get_settings()

    def show_about(self):
        dialog = AboutDialog(self)
        dialog.setMinimumSize(800, 600)  # Устанавливаем минимальный размер
        dialog.exec_()

    def show_analysis(self):
        self.main_menu.hide()
        self.analysis_window.show()

    def export_spectral_maps(self):
        """Сохраняет все доступные спектральные карты в отдельную подпапку с описаниями."""
        if not self.analysis_window.current_image_path:
            QtWidgets.QMessageBox.warning(self, "Внимание", "Сначала загрузите изображение.")
            return

        export_dir = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения")
        if not export_dir:
            return
        
        try:
            image = load_image(self.analysis_window.current_image_path)
            indices = compute_indices(image)
            # Создаём уникальную подпапку
            now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            subfolder = os.path.join(export_dir, f"Spectral-Maps-Export-{now}")
            os.makedirs(subfolder, exist_ok=True)
            readme_lines = ["СПЕКТРАЛЬНЫЕ КАРТЫ И ОПИСАНИЯ:\n"]
            for index_name, index_map in indices.items():
                # Сохраняем саму карту
                output_path = os.path.join(subfolder, f"{index_name}.png")
                generate_heatmap(index_map, output_path)
                # Приводим имя к нижнему регистру для поиска описания
                desc_key = index_name.lower().replace('_emp','').replace('cive','civi').replace('exg','exg').replace('mgrvi','mgrvi').replace('ndvi','ndvi')
                desc = None
                for k in SPECTRAL_INDEX_DESCRIPTIONS:
                    if k.lower() == desc_key:
                        desc = SPECTRAL_INDEX_DESCRIPTIONS[k]
                        break
                # Добавляем описание на отдельную картинку
                import matplotlib.pyplot as plt
                plt.figure(figsize=(10, 6))
                plt.imshow(index_map, cmap='RdYlGn')
                plt.title(desc["name"] if desc else index_name)
                plt.colorbar(label='Значение индекса')
                plt.axis('off')
                # Только описание, без формулы и 'Без описания'
                if desc and desc.get('description'):
                    description = f"{desc['name']}\n\n{desc['description']}"
                    plt.figtext(0.5, 0.01, description, wrap=True, fontsize=9, ha='center', va='bottom', bbox={'facecolor':'white', 'alpha':0.7, 'pad':6})
                desc_path = os.path.join(subfolder, f"{index_name}_desc.png")
                plt.savefig(desc_path, bbox_inches='tight', dpi=200)
                plt.close()
                # Для README
                if desc and desc.get('description'):
                    readme_lines.append(f"{index_name}: {desc['name']}\n{desc['description']}\n")
                else:
                    readme_lines.append(f"{index_name}\n")
            # Сохраняем README.txt
            with open(os.path.join(subfolder, "README.txt"), "w", encoding="utf-8") as f:
                f.write("\n".join(readme_lines))
            QtWidgets.QMessageBox.information(
                self,
                "Готово",
                TRANSLATIONS[self.current_language]["spectral_maps_exported"].format(subfolder)
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Ошибка",
                TRANSLATIONS[self.current_language]["spectral_maps_error"].format(str(e))
            )

    def on_language_combo_changed(self, idx):
        lang = self.main_menu.lang_combo.currentText()
        self.change_language(lang)

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()