import click

from flask.cli import FlaskGroup, with_appcontext

from OLD.monolith.app import create_app
from OLD.monolith.app.extensions import db


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

