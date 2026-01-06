from flask import Blueprint, jsonify, request

from ..models import AnalysisRun, Imagery
from ..schemas import AnalysisRunSchema
from ..services import get_analysis_service
from ...tasks.analysis import run_analysis_task

bp = Blueprint("analysis", __name__)
analysis_schema = AnalysisRunSchema()
analysis_list_schema = AnalysisRunSchema(many=True)


@bp.route("", methods=["GET"])
def list_runs():
    runs = AnalysisRun.query.order_by(AnalysisRun.created_at.desc()).all()
    return jsonify(analysis_list_schema.dump(runs))


@bp.route("/<run_id>", methods=["GET"])
def get_run(run_id):
    run = AnalysisRun.query.get_or_404(run_id)
    return analysis_schema.jsonify(run)


@bp.route("", methods=["POST"])
def create_run():
    payload = request.get_json() or {}
    imagery_id = payload.get("imagery_id")
    if not imagery_id:
        return jsonify({"error": "imagery_id обязателен"}), 400

    index_type = payload.get("index_type", "NDVI_emp")
    options = payload.get("options") or {}
    auto_report = bool(payload.get("auto_report", False))

    imagery = Imagery.query.get_or_404(imagery_id)
    service = get_analysis_service()
    run = service.create_run(imagery, index_type, options)

    run_analysis_task.delay(run.id, auto_report)
    return analysis_schema.jsonify(run), 202

