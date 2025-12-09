from datetime import datetime
from uuid import uuid4

from sqlalchemy import event

from .extensions import db


def generate_uuid():
    return str(uuid4())


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class Imagery(TimestampMixin, db.Model):
    __tablename__ = "imagery"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    original_filename = db.Column(db.String(255))
    stored_path = db.Column(db.String(512), nullable=False)
    captured_at = db.Column(db.DateTime)
    gps_lat = db.Column(db.Float)
    gps_lon = db.Column(db.Float)
    status = db.Column(db.String(32), default="uploaded", nullable=False)
    metadata = db.Column(db.JSON, default=dict)

    analysis_runs = db.relationship(
        "AnalysisRun",
        back_populates="imagery",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class AnalysisRun(TimestampMixin, db.Model):
    __tablename__ = "analysis_run"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    imagery_id = db.Column(
        db.String(36), db.ForeignKey("imagery.id", ondelete="CASCADE"), nullable=False
    )
    status = db.Column(db.String(32), default="pending", nullable=False)
    index_type = db.Column(db.String(32), default="NDVI_emp", nullable=False)
    options = db.Column(db.JSON, default=dict)
    stats = db.Column(db.JSON)
    error_message = db.Column(db.Text)

    imagery = db.relationship("Imagery", back_populates="analysis_runs")
    heatmap = db.relationship(
        "Heatmap",
        uselist=False,
        back_populates="analysis_run",
        cascade="all, delete-orphan",
    )
    report = db.relationship(
        "Report",
        uselist=False,
        back_populates="analysis_run",
        cascade="all, delete-orphan",
    )


class Heatmap(TimestampMixin, db.Model):
    __tablename__ = "heatmap"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    analysis_run_id = db.Column(
        db.String(36),
        db.ForeignKey("analysis_run.id", ondelete="CASCADE"),
        nullable=False,
    )
    index_type = db.Column(db.String(32), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    min_value = db.Column(db.Float)
    max_value = db.Column(db.Float)

    analysis_run = db.relationship("AnalysisRun", back_populates="heatmap")


class Report(TimestampMixin, db.Model):
    __tablename__ = "report"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    analysis_run_id = db.Column(
        db.String(36),
        db.ForeignKey("analysis_run.id", ondelete="CASCADE"),
        nullable=False,
    )
    summary = db.Column(db.Text)
    file_path = db.Column(db.String(512), nullable=False)

    analysis_run = db.relationship("AnalysisRun", back_populates="report")


@event.listens_for(AnalysisRun, "before_update")
def update_timestamp(mapper, connection, target):
    target.updated_at = datetime.utcnow()


