"""Builder for complex PDF reports."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


@dataclass
class ReportPayload:
    """Structured data required for PDF report."""

    pdf_path: str
    original_image_path: str
    heatmap_image_path: str
    report_text: str
    gps_text: str
    index_type: str


class ReportBuilder:
    """Builder accumulates PDF drawing steps."""

    def __init__(self, payload: ReportPayload):
        self.payload = payload
        self.canvas = canvas.Canvas(payload.pdf_path, pagesize=A4)
        self.width, self.height = A4

    def add_header(self):
        self.canvas.setFont("DejaVuSans", 20)
        self.canvas.drawCentredString(
            self.width / 2, self.height - 50, "Отчет по анализу состояния поля"
        )
        self.canvas.setFont("DejaVuSans", 12)
        current_date = datetime.now().strftime("%d.%m.%Y %H:%M")
        self.canvas.drawCentredString(
            self.width / 2, self.height - 70, f"Дата анализа: {current_date}"
        )

    def add_images(self):
        try:
            self.canvas.drawImage(
                self.payload.original_image_path,
                50,
                self.height - 350,
                width=250,
                height=250,
                preserveAspectRatio=True,
            )
            self.canvas.drawString(50, self.height - 360, "Исходное изображение")
        except Exception:
            self.canvas.drawString(50, self.height - 350, "Нет исходного изображения.")
        try:
            self.canvas.drawImage(
                self.payload.heatmap_image_path,
                320,
                self.height - 350,
                width=250,
                height=250,
                preserveAspectRatio=True,
            )
            self.canvas.drawString(
                320, self.height - 360, f"Тепловая карта ({self.payload.index_type})"
            )
        except Exception:
            self.canvas.drawString(320, self.height - 350, "Нет тепловой карты.")

    def add_results(self):
        text_obj = self.canvas.beginText()
        text_obj.setTextOrigin(50, self.height - 370)
        text_obj.setFont("DejaVuSans", 12)
        for line in self.payload.report_text.splitlines():
            text_obj.textLine(line)
        self.canvas.drawText(text_obj)

    def add_gps(self):
        self.canvas.drawString(50, 50, self.payload.gps_text)

    def finalize(self):
        self.canvas.showPage()
        self.canvas.save()


class ReportDirector:
    """Director orchestrates builder steps in a fixed order."""

    def __init__(self, builder: ReportBuilder):
        self.builder = builder

    def build(self):
        self.builder.add_header()
        self.builder.add_images()
        self.builder.add_results()
        self.builder.add_gps()
        self.builder.finalize()
