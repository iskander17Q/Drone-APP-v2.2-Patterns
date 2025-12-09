from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()


def init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)

