from flask import Blueprint, jsonify, request

from ..models import Report
from ..schemas import ReportSchema
from ...tasks.report import generate_report_task

bp = Blueprint("reports", __name__)
report_schema = ReportSchema()
report_list_schema = ReportSchema(many=True)


@bp.route("", methods=["GET"])
def list_reports():
    reports = Report.query.order_by(Report.created_at.desc()).all()
    return jsonify(report_list_schema.dump(reports))


@bp.route("/<report_id>", methods=["GET"])
def get_report(report_id):
    report = Report.query.get_or_404(report_id)
    return report_schema.jsonify(report)


@bp.route("", methods=["POST"])
def create_report():
    payload = request.get_json() or {}
    run_id = payload.get("analysis_run_id")
    if not run_id:
        return jsonify({"error": "analysis_run_id обязателен"}), 400

    generate_report_task.delay(run_id)
    return jsonify({"status": "queued", "analysis_run_id": run_id}), 202

