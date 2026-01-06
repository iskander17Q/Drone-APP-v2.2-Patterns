from flask import Blueprint, jsonify, request

from ..schemas import ImagerySchema
from ..services import get_imagery_service

bp = Blueprint("imagery", __name__)
imagery_schema = ImagerySchema()
imagery_list_schema = ImagerySchema(many=True)


@bp.route("", methods=["GET"])
def list_imagery():
    service = get_imagery_service()
    items = service.list_imagery()
    return jsonify(imagery_list_schema.dump(items))


@bp.route("/<imagery_id>", methods=["GET"])
def get_imagery(imagery_id):
    service = get_imagery_service()
    imagery = service.get(imagery_id)
    return imagery_schema.jsonify(imagery)


@bp.route("", methods=["POST"])
def create_imagery():
    file = request.files.get("file")
    metadata = request.form.to_dict()
    service = get_imagery_service()
    imagery = service.create_from_upload(file, metadata)
    return imagery_schema.jsonify(imagery), 201

