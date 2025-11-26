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
    app = Flask(__name__, instance_relative_config=True)

    # --- KONFIGURACJA ŚCIEŻEK DLA DOCKERA ---
    # Używamy ścieżki /shared, którą zdefiniowaliśmy w docker-compose.yaml
    SHARED_FOLDER = "/shared"
    RESULTS_FOLDER = os.path.join(SHARED_FOLDER, "results")

    # Tworzenie folderów (bezpiecznie)
    try:
        os.makedirs(app.instance_path, exist_ok=True)
        os.makedirs(os.path.join(app.instance_path, "uploads"), exist_ok=True)
        os.makedirs(os.path.join(app.instance_path, "processed"), exist_ok=True)

        # Folder na wyniki Celery
        os.makedirs(RESULTS_FOLDER, exist_ok=True)
        os.chmod(RESULTS_FOLDER, 0o777)  # Pełne uprawnienia dla workera i flaska
    except OSError:
        pass

    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
        CELERY=dict(
            broker_url=os.environ.get(
                "CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672/"
            ),
            # --- KLUCZOWA ZMIANA: BACKEND PLIKOWY ---
            result_backend=f"file://{RESULTS_FOLDER}",
            task_ignore_result=False,
            task_acks_late=True,
            worker_prefetch_multiplier=1,
            worker_concurrency=1,
        ),
        START_TIME=START_TIME,
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

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

    from . import image

    app.register_blueprint(image.bp)

    app.add_url_rule("/", endpoint="index")

    return app
