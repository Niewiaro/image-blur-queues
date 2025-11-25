import sqlite3
from datetime import datetime

import click
from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


@click.command("init-db")
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


@click.command("seed-db")
def seed_db_command():
    """Insert initial users and posts."""
    from werkzeug.security import generate_password_hash

    db = get_db()

    # users
    db.execute(
        "INSERT INTO user (username, password) VALUES (?, ?)",
        ("admin", generate_password_hash("admin")),
    )
    db.execute(
        "INSERT INTO user (username, password) VALUES (?, ?)",
        ("user", generate_password_hash("user")),
    )

    # posts
    admin_id = db.execute(
        "SELECT id FROM user WHERE username = ?", ("admin",)
    ).fetchone()["id"]

    user_id = db.execute(
        "SELECT id FROM user WHERE username = ?", ("user",)
    ).fetchone()["id"]

    db.execute(
        "INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)",
        (
            "Welcome to the Flask app!",
            "Hello everyone! Feel free to explore and enjoy this simple Flask application.",
            admin_id,
        ),
    )

    db.execute(
        "INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)",
        (
            "Flask is cool",
            "I really like using Flask — it is simple and fun to work with!",
            user_id,
        ),
    )

    db.commit()
    click.echo("Seeded database.")


sqlite3.register_converter("timestamp", lambda v: datetime.fromisoformat(v.decode()))


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(seed_db_command)
