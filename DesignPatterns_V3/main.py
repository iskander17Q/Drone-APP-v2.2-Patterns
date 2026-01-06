import os
import sys
import datetime

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from patterns import AnalysisFacade, AppSettings
from patterns.adapter import GPSData
from patterns.observer import SettingsObserver
from utils import get_gps_from_image
from resources import (
    BUTTON_STYLE,
    MENU_STYLE,
    MAIN_WINDOW_STYLE,
    CROP_THRESHOLDS,
    TRANSLATIONS,
    SPECTRAL_INDEX_DESCRIPTIONS,
)

class MainMenu(QtWidgets.QWidget):
    def __init__(self, app_settings: AppSettings, parent=None):
        super().__init__(parent)
        self.settings = app_settings
        self.settings.register(self)
        self.setup_ui()

    def setup_ui(self):
        current_lang = self.settings.language
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(20)

        # Абсолютный слой для выбора языка (только текст)
        lang_widget = QtWidgets.QWidget(self)
        lang_layout = QtWidgets.QHBoxLayout()
        lang_layout.setContentsMargins(0, 0, 10, 0)
        lang_layout.addStretch()
        self.lang_combo = QtWidgets.QComboBox()
        self.lang_combo.addItems(["Русский", "Română"])
        self.lang_combo.setCurrentText(current_lang)
        self.lang_combo.setMinimumWidth(160)
        self.lang_combo.setMaximumWidth(180)
        self.lang_combo.setStyleSheet("background: white; color: #222; border: 2px solid #2E7D32; border-radius: 6px; font-size: 15px; padding: 4px 12px;")
        self.lang_combo.setToolTip("Выберите язык интерфейса / Select language")
        self.lang_combo.currentTextChanged.connect(self._on_language_changed)
        lang_layout.addWidget(self.lang_combo)
        lang_widget.setLayout(lang_layout)
        lang_widget.setFixedHeight(40)
        lang_widget.setFixedWidth(170)
        lang_widget.move(self.width() - 180, 20)
        lang_widget.setStyleSheet("background: transparent;")
        lang_widget.raise_()
        self.lang_widget = lang_widget

        # Заголовок
        self.title = QtWidgets.QLabel(TRANSLATIONS[current_lang]["app_title"])
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2E7D32;")
        self.title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.title)

        # Кнопки главного меню
        self.btn_start = QtWidgets.QPushButton(TRANSLATIONS[current_lang]["start_analysis"])
        self.btn_start.setToolTip("Начать анализ — загрузите снимок и получите результат")
        self.btn_settings = QtWidgets.QPushButton(TRANSLATIONS[current_lang]["settings"])
        self.btn_settings.setToolTip("Настройки анализа и отображения")
        self.btn_about = QtWidgets.QPushButton(TRANSLATIONS[current_lang]["about"])
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
        self.btn_start.setToolTip(TRANSLATIONS[lang]["start_analysis"])
        self.btn_settings.setToolTip(TRANSLATIONS[lang]["settings"])
        self.btn_about.setToolTip(TRANSLATIONS[lang]["about"])

    def showEvent(self, event):
        super().showEvent(event)
        self.lang_combo.setMinimumWidth(160)
        self.lang_combo.setMaximumWidth(180)
        self.lang_combo.updateGeometry()

    def update(self, event, payload):
        if event == "language_changed":
            blocker = QtCore.QSignalBlocker(self.lang_combo)
            self.lang_combo.setCurrentText(payload)
            self.update_language(payload)

    def _on_language_changed(self, lang: str):
        self.settings.set_language(lang)

class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, app_settings: AppSettings, parent=None):
        super().__init__(parent)
        self.app_settings = app_settings
        self.lang_data = TRANSLATIONS[self.app_settings.language]
        self.setWindowTitle(self.lang_data["settings"])
        self.setModal(True)
        self.setup_ui()
        self.setMinimumSize(500, 600)
        self.center_on_screen()

    def setup_ui(self):
        lang = self.lang_data
        layout = QtWidgets.QVBoxLayout()
        self.setStyleSheet("QLabel, QCheckBox { color: #222; } QGroupBox { color: #222; } QDoubleSpinBox { color: #222; } QComboBox { color: #222; background: white; selection-background-color: #E8F5E9; selection-color: #222; border: 1.5px solid #2E7D32; } QPushButton#backBtn { background: white; color: #2E7D32; border: 2px solid #2E7D32; border-radius: 6px; font-size: 14px; padding: 6px 18px; } QPushButton#okBtn { background: #2E7D32; color: white; border: none; border-radius: 6px; font-size: 14px; padding: 8px 28px; }")
        
        # Группа настроек культуры
        crop_group = QtWidgets.QGroupBox(lang["crop_type"])
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
        threshold_group = QtWidgets.QGroupBox(lang["threshold"])
        threshold_layout = QtWidgets.QVBoxLayout()
        
        # Порог стресса
        stress_layout = QtWidgets.QHBoxLayout()
        stress_label = QtWidgets.QLabel(lang["stress_threshold"])
        self.stress_input = QtWidgets.QDoubleSpinBox()
        self.stress_input.setRange(0.0, 1.0)
        self.stress_input.setSingleStep(0.05)
        stress_layout.addWidget(stress_label)
        stress_layout.addWidget(self.stress_input)
        threshold_layout.addLayout(stress_layout)
        
        # Порог растительности
        veg_layout = QtWidgets.QHBoxLayout()
        veg_label = QtWidgets.QLabel(lang["vegetation_threshold"])
        self.veg_input = QtWidgets.QDoubleSpinBox()
        self.veg_input.setRange(0.0, 1.0)
        self.veg_input.setSingleStep(0.05)
        veg_layout.addWidget(veg_label)
        veg_layout.addWidget(self.veg_input)
        threshold_layout.addLayout(veg_layout)
        
        # Примечание
        note_label = QtWidgets.QLabel(lang["threshold_note"])
        note_label.setWordWrap(True)
        note_label.setStyleSheet("font-size: 11px; color: #444;")
        threshold_layout.addWidget(note_label)
        
        threshold_group.setLayout(threshold_layout)
        layout.addWidget(threshold_group)
        
        # Группа дополнительных настроек
        advanced_group = QtWidgets.QGroupBox(lang["settings"])
        advanced_layout = QtWidgets.QVBoxLayout()
        self.auto_boundaries = QtWidgets.QCheckBox(lang["auto_boundaries"])
        advanced_layout.addWidget(self.auto_boundaries)
        self.enhance_contrast = QtWidgets.QCheckBox(lang["enhance_contrast"])
        advanced_layout.addWidget(self.enhance_contrast)
        # Мультиспектральная камера
        self.multispectral = QtWidgets.QCheckBox(lang["multispectral_camera"])
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
        current = self.app_settings.analysis_options.to_dict()
        crop = current.get("crop", list(CROP_THRESHOLDS.keys())[0])
        self.crop_combo.setCurrentText(crop)
        self.update_thresholds(crop)
        self.stress_input.setValue(current.get("stress", CROP_THRESHOLDS[crop]["stressed"]))
        self.veg_input.setValue(current.get("veg", CROP_THRESHOLDS[crop]["healthy"]))
        self.auto_boundaries.setChecked(current.get("auto_boundaries", False))
        self.enhance_contrast.setChecked(current.get("enhance_contrast", False))
        self.multispectral.setChecked(current.get("multispectral", False))
        self.crop_combo.currentTextChanged.connect(self.update_thresholds)

    def update_thresholds(self, crop_type):
        if crop_type in CROP_THRESHOLDS:
            thresholds = CROP_THRESHOLDS[crop_type]
            self.stress_input.setValue(thresholds["stressed"])
            self.veg_input.setValue(thresholds["healthy"])
            self.crop_description.setText(thresholds["description"])

    def get_settings(self):
        settings = {
            "crop": self.crop_combo.currentText(),
            "stress": self.stress_input.value(),
            "veg": self.veg_input.value(),
            "auto_boundaries": self.auto_boundaries.isChecked(),
            "enhance_contrast": self.enhance_contrast.isChecked(),
            "multispectral": self.multispectral.isChecked()
        }
        self.app_settings.update_analysis_options(settings)
        return settings

    def center_on_screen(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

class AboutDialog(QtWidgets.QDialog):
    def __init__(self, app_settings: AppSettings, parent=None):
        super().__init__(parent)
        self.app_settings = app_settings
        self.lang_data = TRANSLATIONS[self.app_settings.language]
        self.setWindowTitle(self.lang_data["about"])
        self.setModal(True)
        self.setup_ui()
        self.setMinimumSize(800, 600)
        self.center_on_screen()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout()
        text_edit = QtWidgets.QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setHtml(self.lang_data["about_text"])
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
    def __init__(
        self,
        app_settings: AppSettings,
        facade: AnalysisFacade,
        parent=None,
    ):
        super().__init__(parent)
        self.app_settings = app_settings
        self.facade = facade
        self.app_settings.register(self)
        self.current_image_path = None
        self.current_result = None
        self.current_gps = None
        self.setup_ui()
        self.apply_language()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout()
        
        # Панель кнопок (верхняя)
        button_layout = QtWidgets.QHBoxLayout()
        
        # Добавляем кнопку возврата в главное меню
        self.btn_back = QtWidgets.QPushButton()
        self.btn_back.clicked.connect(self.back_to_menu)
        button_layout.addWidget(self.btn_back)
        
        self.btn_load = QtWidgets.QPushButton()
        self.btn_load.clicked.connect(self.load_image_file)
        button_layout.addWidget(self.btn_load)
        
        self.btn_analyze = QtWidgets.QPushButton()
        self.btn_analyze.clicked.connect(self.analyze_image)
        self.btn_analyze.setEnabled(False)
        button_layout.addWidget(self.btn_analyze)
        
        self.btn_save = QtWidgets.QPushButton()
        self.btn_save.clicked.connect(self.save_report)
        self.btn_save.setEnabled(False)
        button_layout.addWidget(self.btn_save)
        
        layout.addLayout(button_layout)
        
        # Отображение изображений
        images_layout = QtWidgets.QHBoxLayout()
        
        # Исходное изображение
        original_layout = QtWidgets.QVBoxLayout()
        self.label_original = QtWidgets.QLabel()
        self.label_original.setAlignment(QtCore.Qt.AlignCenter)
        self.label_original.setFixedHeight(400)
        self.label_original.setStyleSheet("border: 1px solid #CCCCCC; border-radius: 4px;")
        original_layout.addWidget(self.label_original)
        images_layout.addLayout(original_layout)
        
        # Тепловая карта
        heatmap_layout = QtWidgets.QVBoxLayout()
        self.label_heatmap = QtWidgets.QLabel()
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
            self._render_pixmap(self.label_original, file_path)
            
            self.label_heatmap.clear()
            self.label_heatmap.setText(TRANSLATIONS[self.app_settings.language]["heatmap"])
            self.text_report.clear()
            self.btn_save.setEnabled(False)
            self.current_result = None
            
            self.btn_analyze.setEnabled(True)
            # Попытка извлечь GPS-данные
            self.current_gps = get_gps_from_image(file_path)
            gps_text = GPSData(
                latitude=self.current_gps.get("latitude") if self.current_gps else None,
                longitude=self.current_gps.get("longitude") if self.current_gps else None,
            ).to_display()
            # Исправляем отображение GPS-информации
            main_window = self.window()
            if isinstance(main_window, QtWidgets.QMainWindow):
                main_window.statusBar().showMessage(gps_text)

    def analyze_image(self):
        """Запускает анализ индексов и отображает тепловую карту."""
        if not self.current_image_path:
            return
        
        try:
            os.makedirs("assets", exist_ok=True)
            heatmap_filename = os.path.join("assets", "heatmap_temp.png")
            result = self.facade.analyze_image(
                self.current_image_path,
                index_type="NDVI_emp",
                options=self.app_settings.analysis_options,
                heatmap_path=heatmap_filename,
            )
            self.current_result = result
            self._render_pixmap(self.label_heatmap, result.heatmap_path)
            report_text = self._build_report_text(result.stats, result.conclusion)
            self.text_report.setText(report_text)
            self.btn_save.setEnabled(True)
        except Exception as exc:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка при анализе: {str(exc)}")

    def back_to_menu(self):
        """Возврат в главное меню."""
        self.hide()
        main_window = self.window()
        if isinstance(main_window, QtWidgets.QMainWindow):
            main_window.main_menu.show()

    def save_report(self):
        """Сохраняет PDF-отчет и экспортирует все спектральные карты в подпапку рядом с PDF."""
        if not self.current_image_path or not self.current_result:
            return
        pdf_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            TRANSLATIONS[self.app_settings.language]["save_report"],
            "",
            "PDF Files (*.pdf)"
        )
        if pdf_path:
            try:
                self.facade.export_report(
                    pdf_path,
                    self.current_result,
                    self.current_image_path,
                    self.text_report.toPlainText(),
                    self.current_gps,
                )
                export_dir = os.path.splitext(pdf_path)[0] + "_spectral_maps"
                self.facade.export_indices(
                    self.current_image_path,
                    export_dir,
                    options=self.app_settings.analysis_options,
                )
                QtWidgets.QMessageBox.information(
                    self,
                    "Успех",
                    TRANSLATIONS[self.app_settings.language]["export_success"]
                    + f"\nПапка с анализами: {export_dir}",
                )
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Ошибка",
                    TRANSLATIONS[self.app_settings.language]["export_error"].format(str(e)),
                )

    def apply_language(self):
        lang = TRANSLATIONS[self.app_settings.language]
        self.btn_back.setText(lang["back_to_menu"])
        self.btn_load.setText(lang["load_image"])
        self.btn_analyze.setText(lang["analyze"])
        self.btn_save.setText(lang["save_report"])
        if self.label_original.pixmap() is None:
            self.label_original.setText(lang["original_image"])
        if self.label_heatmap.pixmap() is None:
            self.label_heatmap.setText(lang["heatmap"])

    def update(self, event, payload):
        if event == "language_changed":
            self.apply_language()
        elif event == "analysis_options_updated":
            self.current_result = None
            if self.current_image_path:
                self.btn_analyze.setEnabled(True)
            self.btn_save.setEnabled(False)

    def _render_pixmap(self, label: QtWidgets.QLabel, image_path: str):
        pixmap = QtGui.QPixmap(image_path)
        if pixmap.isNull():
            label.setText("Не удалось отобразить изображение.")
            return
        if pixmap.width() > label.width() or pixmap.height() > label.height():
            pixmap = pixmap.scaled(
                label.size(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation,
            )
        label.setPixmap(pixmap)

    def _build_report_text(self, stats, conclusion):
        report_text = "Распределение состояния растений:\n"
        for category, pct in stats.items():
            report_text += f"{category}: {pct:.1f}%\n"
        report_text += "\nВывод: " + conclusion
        return report_text

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.app_settings = AppSettings()
        self.app_settings.register(self)
        self.facade = AnalysisFacade()
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        self.setWindowTitle(TRANSLATIONS[self.app_settings.language]["app_title"])
        self.setGeometry(100, 100, 1200, 800)
        
        # Центральный виджет и основной layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Главное меню
        self.main_menu = MainMenu(self.app_settings)
        main_layout.addWidget(self.main_menu)
        
        # Окно анализа (изначально скрыто)
        self.analysis_window = AnalysisWindow(self.app_settings, self.facade, self)
        self.analysis_window.hide()
        main_layout.addWidget(self.analysis_window)
        
        # Подключаем сигналы кнопок главного меню
        self.main_menu.btn_start.clicked.connect(self.show_analysis)
        self.main_menu.btn_settings.clicked.connect(self.show_settings)
        self.main_menu.btn_about.clicked.connect(self.show_about)
        # Подключаем сигнал выбора языка
        # выбор языка обрабатывается через AppSettings наблюдателей
        
        # Создаём меню
        self.create_menus()
        
        # Добавляем строку состояния
        self.statusBar().showMessage("")

    def create_menus(self):
        menu_bar = self.menuBar()
        menu_bar.clear()
        lang = self.app_settings.language
        
        # Меню "Файл"
        file_menu = menu_bar.addMenu("Файл")
        
        action_save_pdf = QtWidgets.QAction(TRANSLATIONS[lang]["save_report"], self)
        action_save_pdf.triggered.connect(self.analysis_window.save_report)
        file_menu.addAction(action_save_pdf)
        
        # Меню "Настройки"
        settings_menu = menu_bar.addMenu(TRANSLATIONS[lang]["settings"])
        
        action_settings = QtWidgets.QAction(TRANSLATIONS[lang]["settings"], self)
        action_settings.triggered.connect(self.show_settings)
        settings_menu.addAction(action_settings)
        
        # Подменю выбора языка (в правом верхнем углу)
        language_menu = menu_bar.addMenu(TRANSLATIONS[lang]["language"])
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
        about_menu = menu_bar.addMenu(TRANSLATIONS[lang]["about"])
        
        action_about = QtWidgets.QAction(TRANSLATIONS[lang]["about"], self)
        action_about.triggered.connect(self.show_about)
        about_menu.addAction(action_about)

    def apply_styles(self):
        self.setStyleSheet(MAIN_WINDOW_STYLE)
        self.menuBar().setStyleSheet(MENU_STYLE)
        
        for button in self.findChildren(QtWidgets.QPushButton):
            button.setStyleSheet(BUTTON_STYLE)

    def change_language(self, language):
        self.app_settings.set_language(language)

    def show_settings(self):
        dialog = SettingsDialog(self.app_settings, self)
        dialog.exec_()

    def show_about(self):
        dialog = AboutDialog(self.app_settings, self)
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
            now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            subfolder = os.path.join(export_dir, f"Spectral-Maps-Export-{now}")
            self.facade.export_indices(
                self.analysis_window.current_image_path,
                subfolder,
                options=self.app_settings.analysis_options,
            )
            QtWidgets.QMessageBox.information(
                self,
                "Готово",
                TRANSLATIONS[self.app_settings.language]["spectral_maps_exported"].format(subfolder)
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Ошибка",
                TRANSLATIONS[self.app_settings.language]["spectral_maps_error"].format(str(e))
            )

    def update(self, event, payload):
        if event == "language_changed":
            self.setWindowTitle(TRANSLATIONS[payload]["app_title"])
            self.create_menus()

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()
