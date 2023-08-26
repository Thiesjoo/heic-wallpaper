from datetime import datetime
import json
import os
import time
from uuid import uuid4
from flask import (
    Flask,
    jsonify,
    redirect,
    request,
    url_for,
    current_app,
    g as app_ctx,
)
from backend.config import AppConfig
from backend.worker.image_processor import handle_all_images
from backend.tasks import amount_of_pending_tasks, tasks
from werkzeug.utils import secure_filename

from backend.database.redis import (
    Wallpaper,
    WallpaperStatus,
    WallpaperType,
    add_wallpaper,
    get_all_wallpapers,
    get_single_wallpaper,
)

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://169d60844720489392d6fa7c6d33215f@o4504384319258624.ingest.sentry.io/4504384322600963",
    integrations=[
        FlaskIntegration(),
    ],
    traces_sample_rate=1.0,
)


ALLOWED_EXTENSIONS = {"heic", "png", "jpg", "jpeg"}


def get_extension(filename):
    return filename.rsplit(".", 1)[1].lower()

def detemine_type_from_extension(extension):
    if extension == "heic":
        return WallpaperType.HEIC
    else:
        return WallpaperType.GENERIC

def allowed_file(filename):
    return "." in filename and get_extension(filename) in ALLOWED_EXTENSIONS


PRODUCTION = bool(os.environ.get("PRODUCTION", False))

os.makedirs(os.path.join(AppConfig.STATIC_FOLDER), exist_ok=True)
os.makedirs(os.path.join(AppConfig.UPLOAD_FOLDER), exist_ok=True)
os.makedirs(os.path.join(AppConfig.PROCESSED_FOLDER), exist_ok=True)

app = Flask(
    __name__,
    static_folder=AppConfig.STATIC_FOLDER,
)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 300

app.config["UPLOAD_FOLDER"] = AppConfig.UPLOAD_FOLDER


# Max size is 100mb
app.config["MAX_CONTENT_LENGTH"] = 100 * 1000 * 1000

app.register_blueprint(tasks, url_prefix="/api/tasks")


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


@app.route("/api/fixupredis")
def fixup_redis():
    if amount_of_pending_tasks() != 0:
        return "There are still pending tasks, please wait a bit", 409

    for filename in os.scandir(AppConfig.PROCESSED_FOLDER):
        try:
            if not filename.is_dir():
                app.logger.warn(f"Non file found inside processed dir: {filename.path}")
                continue
            org = get_single_wallpaper(filename.name)
            app.logger.info(f"Reimporting file: {filename.name}")
            if not (type(org) == tuple):
                app.logger.info("Already exists in redis")
                continue

            f = open(f"{filename.path}/data.json")
            data = json.loads(f.read())

            add_wallpaper(filename.name, data)
        except Exception as e:
            app.logger.error(f"Error while importing {filename.name}: {e}")
            continue
    return "Redis is now in sync with the file system!"


@app.route("/api/upload", methods=["POST"])
def upload_new_wallpaper():
    user = request.headers.get("x-user")
    print(user)
    if PRODUCTION and user is None:
        return "You need to be logged in to upload a wallpaper", 401
    else:
        user = "unknown"

    # check if the post request has the file part
    if "file" not in request.files:
        return "You are missing the file", 400
    file = request.files["file"]
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == "" or not file:
        return "You didn't select a file", 400
    if file and allowed_file(file.filename):
        uid = str(uuid4())
        new_filename = f"{uid}.{get_extension(file.filename)}"
        app.logger.info(f"Uploading new file with name {new_filename}")

        file.save(os.path.join(app.config["UPLOAD_FOLDER"], new_filename))

        app.logger.info(
            f"File should be uploaded to {f'{AppConfig.UPLOAD_FOLDER}/{new_filename}'}: {os.path.exists(f'{AppConfig.UPLOAD_FOLDER}/{new_filename}')}"
        )

        old_name = secure_filename(file.filename)

        add_wallpaper(
            uid,
            {
                "uid": uid,
                "original_name": old_name,
                "created_by": user,
                "date_created": int(time.time()),
                "status": WallpaperStatus.PROCESSING,
                "type": WallpaperType.HEIC,
                "data": {},
                "error": None
            },
        )

        task = handle_all_images.delay(new_filename, uid, old_name, detemine_type_from_extension(get_extension(file.filename)))
        return jsonify(
            {"taskid": url_for("tasks.single_task_status", task_id=task.id), "ok": True}
        )
    return "This is not a valid extension", 400

@app.route("/api/delete_pending")
def delete_pending():
    if amount_of_pending_tasks() != 0:
        return "There are still pending tasks, please wait a bit", 409

    delete_pending()

    return "Redis is now in sync with the file system!"

def wallpaper_mapper(wallpaper: Wallpaper, extended=False):
    to_return = {
        "name": wallpaper["original_name"],
        "id": wallpaper["uid"],
        "created_by": wallpaper["created_by"] if "created_by" in wallpaper else "Unknown",
        "location": url_for("get_wallpaper", uid=wallpaper["uid"]),
        "preview_url": url_for(
            "static", filename=f"processed/{wallpaper['uid']}/preview.png"
        ),
        "status": wallpaper["status"],
        "error": wallpaper["error"] if "error" in wallpaper else None,
        "type": wallpaper["type"],
    }

    if extended:
        to_return["data"] = wallpaper["data"]

    return to_return


@app.route("/api/wallpapers")
def get_wallpapers():
    all_wallpaper_data = get_all_wallpapers()
    wallpapers = [wallpaper_mapper(wallpaper) for wallpaper in all_wallpaper_data]
    return jsonify(wallpapers)


@app.route("/api/wallpaper/<string:uid>")
def get_wallpaper(uid: str):
    wallpaper = get_single_wallpaper(uid)
    if type(wallpaper) == tuple:
        return wallpaper

    if wallpaper is None:
        return "This wallpaper is not in my system", 404

    times = wallpaper["data"]

    if times is None:
        return redirect(url_for("static", filename=f"processed/{uid}/0.png"))

    now = datetime.now().time()
    nowsecs = now.hour * 60 * 60 + now.minute * 60 + now.second

    # https://github.com/mczachurski/wallpapper
    last_one = times[-1]
    for time in times:
        if nowsecs > float(time["t"]) * 60 * 60 * 24:
            last_one = time
    index = last_one["i"]

    return redirect(url_for("static", filename=f"processed/{uid}/{index}.png"))

@app.route("/api/wallpaper/<string:uid>/details")
def get_wallpaper_information(uid: str):
    wallpaper = get_single_wallpaper(uid)
    if type(wallpaper) == tuple:
        return wallpaper
    return wallpaper_mapper(wallpaper, extended=True)