from datetime import datetime
import json
import os
from uuid import uuid4
from flask import Flask, jsonify, redirect, request, url_for
from config import AppConfig
from workers.image_processor import func1, handle_image
from tasks import tasks
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"heic", "png", "jpg", "jpeg", "gif"}


def get_extension(filename):
    return filename.rsplit(".", 1)[1].lower()


def allowed_file(filename):
    return "." in filename and get_extension(filename) in ALLOWED_EXTENSIONS


app = Flask(
    __name__,
    static_folder="/static/",
)
app.config["UPLOAD_FOLDER"] = AppConfig.UPLOAD_FOLDER
os.makedirs(os.path.join(AppConfig.UPLOAD_FOLDER), exist_ok=True)
os.makedirs(os.path.join(AppConfig.PROCESSED_FOLDER), exist_ok=True)


# Max size is 100mb
app.config["MAX_CONTENT_LENGTH"] = 100 * 1000 * 1000

app.register_blueprint(tasks)


@app.route("/")
def hello_world():
    task = func1.delay(1)
    return jsonify({"taskid": url_for("tasks.taskstatus", task_id=task.id), "ok": True})


@app.route("/upload", methods=["POST"])
def upload_new_wallpaper():
    # check if the post request has the file part
    if "file" not in request.files:
        return "You are missing the file", 400
    file = request.files["file"]
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == "" or not file:
        return "You didn't select a file", 400
    if file and allowed_file(file.filename):
        new_filename = f"{str(uuid4())}.{get_extension(file.filename)}"
        app.logger.info(f"Uploading new file with name {new_filename}")

        file.save(os.path.join(app.config["UPLOAD_FOLDER"], new_filename))
        app.logger.info(
            f"File should be uploaded {os.path.exists(f'{AppConfig.UPLOAD_FOLDER}/{new_filename}')}"
        )
        task = handle_image.delay(new_filename, secure_filename(file.filename))
        return jsonify(
            {"taskid": url_for("tasks.taskstatus", task_id=task.id), "ok": True}
        )
    return "This is not a valid extension", 400


@app.route("/wallpapers")
def get_wallpapers():
    # Returns a list of all available .heic wallpapers with identifiers?
    wallpapers = [
        {
            "name": f.name,
            "preview_url": url_for(
                "static", filename=f"processed/{f.name}/preview.png"
            ),
        }
        for f in os.scandir(f"{AppConfig.PROCESSED_FOLDER}")
    ]
    return jsonify(wallpapers)


@app.route("/wallpaper/<string:name>")
def get_wallpaper(name: str):
    if not name.endswith(".heic"):
        # special logic?
        assert False

    if not os.path.exists(f"{AppConfig.PROCESSED_FOLDER}/{name}"):
        return "Image does not exist", 404

    json_location = f"{AppConfig.PROCESSED_FOLDER}/{name}/data.json"
    with open(json_location, "r") as f:
        data = json.load(f)

        times = data["data"]

    nowsecs = request.args.get("time", type=int)
    if not nowsecs:
        now = datetime.now().time()
        nowsecs = now.hour * 60 * 60 + now.minute * 60 + now.second

    last_one = times[-1]
    for time in times:
        if float(time["t"]) * 60 * 60 * 24 > nowsecs:
            if (
                float(time["t"]) * 60 * 60 * 24 - nowsecs < 10
            ):  # prevent floating errors or similar things
                last_one = time
            break
        last_one = time
    index = last_one["i"]

    return redirect(url_for("static", filename=f"processed/{name}/{index}.png"))


# Returns a URL (which nginx? should serve) for a specific name and a specific time
