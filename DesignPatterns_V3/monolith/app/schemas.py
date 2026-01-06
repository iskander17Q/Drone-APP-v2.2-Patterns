from marshmallow import fields

from .extensions import ma
from .models import AnalysisRun, Heatmap, Imagery, Report


class HeatmapSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Heatmap
        load_instance = True
        include_fk = True


class ReportSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Report
        load_instance = True
        include_fk = True


class AnalysisRunSchema(ma.SQLAlchemyAutoSchema):
    heatmap = fields.Nested(HeatmapSchema)
    report = fields.Nested(ReportSchema)

    class Meta:
        model = AnalysisRun
        load_instance = True
        include_fk = True


class ImagerySchema(ma.SQLAlchemyAutoSchema):
    analysis_runs = fields.Nested(AnalysisRunSchema, many=True, dump_only=True)

    class Meta:
        model = Imagery
        load_instance = True
        include_relationships = True


