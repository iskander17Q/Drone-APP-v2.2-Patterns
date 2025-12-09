from flask import Flask

from .config import Config
from .extensions import init_extensions
from .routes.health import bp as health_bp
from .routes.imagery import bp as imagery_bp
from .routes.analysis import bp as analysis_bp
from .routes.reports import bp as reports_bp
from .services.storage_service import StorageService


def register_blueprints(app: Flask):
    app.register_blueprint(health_bp)
    app.register_blueprint(imagery_bp, url_prefix="/imagery")
    app.register_blueprint(analysis_bp, url_prefix="/analysis-runs")
    app.register_blueprint(reports_bp, url_prefix="/reports")


def create_app(config_object=Config):
    app = Flask(__name__.split(".")[0])
    app.config.from_object(config_object)

    init_extensions(app)
    storage_service = StorageService(app.config["STORAGE_ROOT"])
    storage_service.ensure_directories()
    app.extensions["storage_service"] = storage_service

    register_blueprints(app)
    return app

