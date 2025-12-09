from OLD.utils import generate_pdf_report

from ..models import AnalysisRun, Report


class ReportService:
    def __init__(self, session, storage):
        self.session = session
        self.storage = storage

    def generate_for_run(self, run_id: str) -> Report:
        run = AnalysisRun.query.get(run_id)
        if not run:
            raise ValueError(f"AnalysisRun {run_id} не найден")
        if run.report:
            return run.report
        if run.status != "completed":
            raise ValueError("Анализ ещё не завершён")
        if not run.heatmap:
            raise ValueError("Нет тепловой карты для отчёта")

        pdf_name = f"{run.id}.pdf"
        relative_pdf = self.storage.build_relative("reports", pdf_name)
        absolute_pdf = self.storage.absolute_path(relative_pdf)
        original = self.storage.absolute_path(run.imagery.stored_path)
        heatmap = self.storage.absolute_path(run.heatmap.file_path)

        report_text_lines = [
            f"Анализ {run.id}",
            f"Индекс: {run.index_type}",
            f"Вывод: {run.stats.get('conclusion') if run.stats else 'Нет данных'}",
        ]
        distribution = run.stats.get("distribution") if run.stats else None
        if distribution:
            for key, value in distribution.items():
                report_text_lines.append(f"{key}: {value:.1f}%")

        generate_pdf_report(
            absolute_pdf,
            original,
            heatmap,
            "\n".join(report_text_lines),
            gps={
                "latitude": run.imagery.gps_lat,
                "longitude": run.imagery.gps_lon,
            },
            index_type=run.index_type,
        )

        report = Report(
            analysis_run=run,
            summary="\n".join(report_text_lines),
            file_path=relative_pdf,
        )
        self.session.add(report)
        self.session.commit()
        return report

