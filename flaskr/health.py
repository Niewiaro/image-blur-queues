from flask import Blueprint, jsonify, current_app

bp = Blueprint("health", __name__, url_prefix="/")


def get_database_info():
    """Return basic database health info."""
    from .db import get_db

    db_status = "unknown"

    try:
        db = get_db()
        db.execute("SELECT 1")
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {e}"

    return {"status": db_status}


@bp.route("/healthz")
def healthz():
    """Liveness probe — checks only if the app is running."""
    return jsonify({"status": "ok"}), 200


@bp.route("/readyz")
def readyz():
    """Readiness probe — checks if the app is ready to serve traffic."""
    if get_database_info()["status"] == "ok":
        return jsonify({"status": "ok"}), 200
    return jsonify({"status": "error"}), 500


@bp.route("/health")
def health():
    """
    Full health check — useful for monitoring.
    Includes DB, can include more services in the future.
    """
    checks = {}

    # Database check
    checks["database"] = get_database_info()["status"]

    overall_ok = all(value == "ok" for value in checks.values())

    return jsonify({"status": "ok" if overall_ok else "error", "checks": checks}), (
        200 if overall_ok else 500
    )


@bp.route("/info")
def info():
    from datetime import datetime, timezone
    import platform

    start_time = current_app.config["START_TIME"]
    uptime = datetime.now(timezone.utc) - start_time

    result = {
        "app": current_app.name,
        "system": platform.system(),
        "hostname": platform.node(),
        "uptime": str(uptime),
        "database": get_database_info(),
    }

    return jsonify(result), 200
