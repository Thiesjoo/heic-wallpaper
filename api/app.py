from datetime import datetime
import json
import os
import time
from uuid import uuid4
from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
    current_app,
    g as app_ctx,
)
from config import AppConfig
from workers.image_processor import handle_image
from tasks import tasks
from werkzeug.utils import secure_filename

from database.redis import (
    Wallpaper,
    WallpaperStatus,
    WallpaperTypes,
    add_wallpaper,
    get_all_wallpapers,
    get_single_wallpaper,
)

ALLOWED_EXTENSIONS = {"heic", "png", "jpg", "jpeg", "gif"}


def get_extension(filename):
    return filename.rsplit(".", 1)[1].lower()


def allowed_file(filename):
    return "." in filename and get_extension(filename) in ALLOWED_EXTENSIONS


app = Flask(
    __name__,
    static_folder="/static/",
)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 300

app.config["UPLOAD_FOLDER"] = AppConfig.UPLOAD_FOLDER
os.makedirs(os.path.join(AppConfig.UPLOAD_FOLDER), exist_ok=True)
os.makedirs(os.path.join(AppConfig.PROCESSED_FOLDER), exist_ok=True)

# Max size is 100mb
app.config["MAX_CONTENT_LENGTH"] = 100 * 1000 * 1000

app.register_blueprint(tasks, url_prefix="/tasks")


@app.errorhandler(413)
def too_large(e):
    return "File is too large. Please contact admin for manual upload", 413


@app.before_request
def logging_before():
    # Store the start time for the request
    app_ctx.start_time = time.perf_counter()


@app.after_request
def logging_after(response):
    # Get total time in milliseconds
    total_time = time.perf_counter() - app_ctx.start_time
    time_in_ms = int(total_time * 1000)
    # Log the time taken for the endpoint
    current_app.logger.info(
        "%s ms %s %s %s", time_in_ms, request.method, request.path, dict(request.args)
    )
    return response


@app.route("/")
def index():
    return render_template("index.html")


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
        id = str(uuid4())
        new_filename = f"{id}.{get_extension(file.filename)}"
        app.logger.info(f"Uploading new file with name {new_filename}")

        file.save(os.path.join(app.config["UPLOAD_FOLDER"], new_filename))

        app.logger.info(
            f"File should be uploaded {os.path.exists(f'{AppConfig.UPLOAD_FOLDER}/{new_filename}')}"
        )

        old_name = secure_filename(file.filename)

        add_wallpaper(
            new_filename,
            {
                "original_name": old_name,
                "date_created": int(time.time()),
                "status": WallpaperStatus.PROCESSING,
                "type": WallpaperTypes.HEIC,
            },
        )

        task = handle_image.delay(new_filename, old_name)
        return jsonify(
            {"taskid": url_for("tasks.single_task_status", task_id=task.id), "ok": True}
        )
    return "This is not a valid extension", 400


def wallpaper_mapper(wallpaper: Wallpaper, extended=False):
    to_return = {
        "name": wallpaper["original_name"],
        "pending": not wallpaper["status"] == WallpaperStatus.READY,
        "id": wallpaper["uuid"],
        "location": url_for("get_wallpaper", name=wallpaper["uuid"]),
        "preview_url": url_for(
            "static", filename=f"processed/{wallpaper['uuid']}/preview.png"
        ),
        "status": wallpaper["status"],
        "error": wallpaper["error"] if "error" in wallpaper else None,
    }
    if extended:
        to_return["data"] = wallpaper["data"]
    return to_return


@app.route("/wallpapers")
def get_wallpapers():
    all_wallpaper_data = get_all_wallpapers()
    wallpapers = [wallpaper_mapper(wallpaper) for wallpaper in all_wallpaper_data]
    return jsonify(wallpapers)


@app.route("/wallpaper/<string:name>/preview")
def render_wallpaper_preview(name: str):
    return render_template("wallpaper.html")


@app.route("/wallpaper/<string:name>/details")
def get_wallpaper_information(name: str):
    return wallpaper_mapper(get_single_wallpaper(name), extended=True)


@app.route("/wallpaper/<string:name>")
def get_wallpaper(name: str):
    if not name.endswith(".heic"):
        # special logic? for custom PNG's
        assert False

    wallpaper = get_single_wallpaper(name)
    if type(wallpaper) == tuple:
        return wallpaper

    if wallpaper is None:
        return "This wallpaper is not in my system", 404

    times = wallpaper["data"]

    now = datetime.now().time()
    nowsecs = now.hour * 60 * 60 + now.minute * 60 + now.second

    # https://github.com/mczachurski/wallpapper
    last_one = times[-1]
    for time in times:
        if nowsecs > float(time["t"]) * 60 * 60 * 24:
            last_one = time
    index = last_one["i"]

    return redirect(url_for("static", filename=f"processed/{name}/{index}.png"))
