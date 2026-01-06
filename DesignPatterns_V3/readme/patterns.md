# DesignPatterns_V3 — внедрённые паттерны

Ниже описано, где и зачем используется каждый из десяти паттернов внутри приложения. Все решения встроены в рабочий функционал: GUI и бекенд пользуются одними и теми же компонентами без вспомогательных «учебных» примеров.

## Singleton
- **Класс**: `patterns.settings.AppSettings`
- **Задача**: централизует состояние языка интерфейса и активных параметров анализа.
- **Контекст**: MainWindow, MainMenu, AnalysisWindow и SettingsDialog используют одиночку, поэтому изменения языка/порогов мгновенно доходят до всех окон.

## Observer
- **Классы**: `patterns.observer.Observable`, `SettingsObserver`, плюс виджеты GUI.
- **Задача**: рассылает события `language_changed` и `analysis_options_updated`.
- **Контекст**: MainWindow обновляет меню, AnalysisWindow очищает результаты, MainMenu синхронизирует выпадающий список языка.

## Factory
- **Класс**: `patterns.indices.IndexCalculatorFactory`
- **Задача**: поставляет стратегии вычисления индексов по имени.
- **Контекст**: `SpectralIndexCalculator` и фасад используют фабрику, поэтому добавление нового индекса ограничивается регистрацией стратегии.

## Strategy
- **Классы**: `patterns.indices.SpectralIndexStrategy` + конкретные реализации.
- **Задача**: инкапсулирует разные формулы индексов.
- **Контекст**: `SpectralIndexCalculator.compute_all` перебирает стратегии и возвращает словарь карт для GUI, экспорта и бекенда.

## Builder
- **Классы**: `patterns.report_builder.ReportBuilder`, `ReportDirector`, `ReportPayload`.
- **Задача**: собирает PDF отчёт из нескольких шагов.
- **Контекст**: `utils.generate_pdf_report` и `ReportService` используют билдера — логика формирования страниц отделена от прикладного кода.

## Adapter
- **Классы**: `patterns.adapter.GpsMetadataAdapter`, `GPSData`.
- **Задача**: преобразует сложную структуру EXIF `GPSInfo` в удобные координаты.
- **Контекст**: `utils.get_gps_from_image` возвращает адаптированную структуру; GUI и PDF выводят координаты в одном формате.

## Decorator
- **Классы**: `patterns.image_loader.ImageLoader`, `ImageLoaderDecorator`, `ContrastEnhancementLoader`, `FieldBoundaryFocusLoader`.
- **Задача**: динамически модифицирует загрузку изображений (CLAHE, выделение границ) на основе пользовательских флажков.
- **Контекст**: и GUI, и Celery анализ используют `build_loader`, поэтому поведение строго синхронизировано.

## Proxy
- **Класс**: `patterns.proxy.StorageProxy`
- **Задача**: оборачивает `StorageService`, валидирует относительные пути и логирует работу без изменения оригинального класса.
- **Контекст**: `monolith.app.create_app` публикует в Flask extensions именно прокси, поэтому все сервисы (Imagery, Analysis, Reports) работают через дополнительный защитный слой.

## Facade
- **Класс**: `patterns.facade.AnalysisFacade`
- **Задача**: предоставляет единый API `analyze_image`, `export_report`, `export_indices`.
- **Контекст**: GUI, Celery и CLI используют фасад, поэтому весь пайплайн обработки описан в одном месте.

## Command
- **Классы**: `patterns.command.*Command`
- **Задача**: разделяет пайплайн анализа на независимые шаги (загрузка, индексы, тепловая карта, классификация).
- **Контекст**: `AnalysisFacade._commands()` возвращает последовательность команд, поэтому расширить пайплайн можно добавлением нового объекта.


Эти паттерны работают совместно: Singleton и Observer управляют состоянием, Decorator/Strategy/Factory расширяют вычисления, Command и Facade формируют пайплайн, Adapter/Builder обслуживают вспомогательные процессы, а Proxy защищает файловое хранилище. Благодаря этому анализ изображений выполняется одинаково предсказуемо в GUI и в бекенде.
