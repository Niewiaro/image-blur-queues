import os
import uuid
from flask import (
    Blueprint,
    g,
    request,
    url_for,
    current_app,
    jsonify,
    send_from_directory,
    render_template,
)

from flaskr.tasks import process_image

bp = Blueprint("image", __name__, url_prefix="/image")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/", methods=["GET"])
def index():
    return render_template("image/upload.html")


@bp.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        ext = file.filename.rsplit(".", 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        upload_folder = os.path.join(current_app.instance_path, "uploads")

        os.makedirs(upload_folder, exist_ok=True)
        file.save(os.path.join(upload_folder, unique_filename))

        # LOGIKA PRIORYTETÓW
        if g.user:
            queue_name = "high_priority"
            print(f"--> [FLASK] Użytkownik {g.user['username']} (VIP) -> High Priority")
        else:
            queue_name = "low_priority"
            print("--> [FLASK] Użytkownik anonimowy -> Low Priority")

        task = process_image.apply_async(
            args=[unique_filename, current_app.instance_path], queue=queue_name
        )

        return (
            jsonify(
                {"task_id": task.id, "queue": queue_name, "filename": unique_filename}
            ),
            202,
        )

    return jsonify({"error": "Invalid file type"}), 400


@bp.route("/status/<task_id>")
def task_status(task_id):
    celery_app = current_app.extensions["celery"]  # Pobieramy obiekt z __init__.py
    task_result = celery_app.AsyncResult(task_id)  # Używamy go do sprawdzenia statusu

    print(f"[STATUS] Sprawdzam ID={task_id}, Status={task_result.status}")

    response = {"task_id": task_id, "status": task_result.status}

    if task_result.status == "SUCCESS":
        response["result"] = task_result.result
        # Pobieramy nazwę pliku z wyniku workera
        filename = task_result.result.get("filename")
        if filename:
            response["image_url"] = url_for("image.get_image", filename=filename)
    elif task_result.status == "FAILURE":
        response["error"] = str(task_result.result)

    return jsonify(response)


@bp.route("/result/<filename>")
def get_image(filename):
    return send_from_directory(
        os.path.join(current_app.instance_path, "processed"), filename
    )
