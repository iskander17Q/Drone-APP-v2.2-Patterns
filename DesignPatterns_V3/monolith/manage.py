import sys
from pathlib import Path

import click
from flask.cli import FlaskGroup, with_appcontext

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from app.extensions import db


def create_monolith():
    return create_app()


cli = FlaskGroup(create_app=create_monolith)


@cli.command("init-db")
@with_appcontext
def init_db():
    """Создать все таблицы без Alembic."""
    db.create_all()
    click.echo("База данных инициализирована")


if __name__ == "__main__":
    cli()
