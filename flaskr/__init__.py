import os
from flask import Flask
from datetime import datetime, timezone

START_TIME = datetime.now(timezone.utc)


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )
    app.config["START_TIME"] = START_TIME

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route("/hello")
    def hello():
        return "Hello, World!"

    from . import db

    db.init_app(app)

    from . import health

    app.register_blueprint(health.bp)

    from . import auth

    app.register_blueprint(auth.bp)

    from . import review

    app.register_blueprint(review.bp)
    app.add_url_rule("/", endpoint="index")

    return app
