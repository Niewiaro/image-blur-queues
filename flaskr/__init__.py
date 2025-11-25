import os
from flask import Flask
from celery import Celery, Task
from datetime import datetime, timezone

START_TIME = datetime.now(timezone.utc)


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
        CELERY=dict(
            broker_url=os.environ.get(
                "CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672/"
            ),
            result_backend="rpc://",
            task_ignore_result=True,
        ),
        START_TIME=START_TIME,
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
        os.makedirs(os.path.join(app.instance_path, "uploads"), exist_ok=True)
        os.makedirs(os.path.join(app.instance_path, "processed"), exist_ok=True)
    except OSError:
        pass

    celery_init_app(app)

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

    from . import image

    app.register_blueprint(image.bp)

    return app
