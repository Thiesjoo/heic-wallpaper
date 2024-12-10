import json
import time
from datetime import datetime
from uuid import uuid4

import boto3
import pytz
from flask import Flask, request, url_for, redirect, jsonify
from werkzeug.utils import secure_filename

from backend import jwt_authentik
from backend.config import AppConfig
from backend.database.redis import WallpaperType, add_wallpaper, WallpaperStatus, \
    Wallpaper, get_single_wallpaper, update_status_of_wallpaper, get_all_wallpapers, \
    add_error_to_wallpaper
from backend.tasks import tasks
from backend.worker.image_processor import handle_all_images

from logging.config import dictConfig

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
            }
        },
        "root": {"level": "DEBUG", "handlers": ["console"]},
    }
)

app = Flask(
    __name__,
)
app.register_blueprint(tasks, url_prefix="/api/tasks")

AppConfig.validate()

s3 = boto3.client('s3',
                  endpoint_url=AppConfig.UPLOAD.S3_URL,
                  config=boto3.session.Config(signature_version='s3v4'),
                  aws_access_key_id=AppConfig.UPLOAD.S3_ACCESS_KEY,
                  aws_secret_access_key=AppConfig.UPLOAD.S3_SECRET_KEY,
                  )

s3.put_bucket_lifecycle_configuration(
    Bucket=AppConfig.UPLOAD.BUCKET,
    LifecycleConfiguration={
        'Rules': [
            {
                'ID': 'delete_temp_files',
                'Status': 'Enabled',
                'Filter': {
                    'Prefix': '',
                },
                'Expiration': {
                    'Days': 1,
                },
            },
        ],
    },
)

ALLOWED_EXTENSIONS = {"heic", "png", "jpg", "jpeg"}


def get_extension(filename):
    return filename.rsplit(".", 1)[1].lower()


def determine_type_from_extension(extension):
    if extension == "heic":
        return WallpaperType.HEIC
    else:
        return WallpaperType.GENERIC


def allowed_file(filename):
    return "." in filename and get_extension(filename) in ALLOWED_EXTENSIONS


@app.route("/api/upload", methods=["POST"])
def upload():
    # TODO: login??
    # TODO: Max size
    file_name = request.json.get('name')
    file_type = request.json.get('type')

    if file_name is None or file_type is None:
        return json.dumps({
            'error': 'name and type are required'
        }), 400

    uid = str(uuid4())
    new_filename = f"{uid}.{get_extension(file_name)}"

    presigned_post = s3.generate_presigned_url(
        ClientMethod='put_object',
        Params={
            'Bucket': AppConfig.UPLOAD.BUCKET,
            'Key': new_filename,
            'ContentType': file_type
        },
        ExpiresIn=3600
    )

    old_name = secure_filename(file_name)

    add_wallpaper(
        uid,
        {
            "uid": uid,
            "original_name": old_name,
            "created_by": "TODO: IMPLEMENT THIS",
            "date_created": int(time.time()),
            "status": WallpaperStatus.UPLOADING,
            "type": determine_type_from_extension(get_extension(file_name)),
            "data": {},
            "error": None
        },
    )

    return json.dumps({
        'data': presigned_post,
        'uid': uid,
        'key': new_filename
    })


@app.route("/api/upload/complete", methods=["POST"])
def upload_complete():
    uid = request.json.get('uid')
    key = request.json.get('key')

    if uid is None or key is None:
        return json.dumps({
            'error': 'uid/key is required'
        }), 400

    try:
        s3.head_object(Bucket=AppConfig.UPLOAD.BUCKET, Key=key)
    except Exception as e:
        return json.dumps({
            'error': 'invalid uid/key'
        }), 400

    update_status_of_wallpaper(uid, WallpaperStatus.PROCESSING)
    task = handle_all_images.delay(key, uid, determine_type_from_extension(
        get_extension(key)))
    add_error_to_wallpaper(uid, url_for("tasks.single_task_status", task_id=task.id))

    return json.dumps({
        'data': 'ok',
        "task": url_for("tasks.single_task_status", task_id=task.id)
    }), 202


def _get_url_for_wallpaper(wallpaper: Wallpaper, index: int | str) -> str:
    return f"{AppConfig.PUBLIC_ASSET_URL}/{wallpaper['uid']}/{index}.png"


def wallpaper_mapper(wallpaper: Wallpaper, extended=False):
    to_return = {
        "name": wallpaper["original_name"],
        "id": wallpaper["uid"],
        "created_by": wallpaper[
            "created_by"] if "created_by" in wallpaper else "Unknown",
        "location": url_for("get_wallpaper", uid=wallpaper["uid"]),
        "preview_url": _get_url_for_wallpaper(wallpaper, "preview"),
        "status": wallpaper["status"],
        "error": wallpaper["error"] if "error" in wallpaper else None,
        "type": wallpaper["type"],
        "data": wallpaper["data"]
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
    tz = pytz.utc
    if request.args.get("tz"):
        timezone = request.args.get("tz")
        try:
            tz = pytz.timezone(timezone)
        except pytz.exceptions.UnknownTimeZoneError:
            return "Invalid timezone", 400

    wallpaper = get_single_wallpaper(uid)
    if type(wallpaper) == tuple:
        return wallpaper

    if wallpaper is None:
        return "This wallpaper is not in my system", 404

    times = wallpaper["data"]

    if times is None:
        return redirect(_get_url_for_wallpaper(wallpaper, 0))

    now = datetime.now(tz).time()
    nowsecs = now.hour * 60 * 60 + now.minute * 60 + now.second

    # https://github.com/mczachurski/wallpapper
    last_one = times[-1]
    for time in times:
        if nowsecs > float(time["t"]) * 60 * 60 * 24:
            last_one = time
    index = last_one["i"]

    return redirect(_get_url_for_wallpaper(wallpaper, index))


@app.route("/api/wallpaper/<string:uid>/details")
def get_wallpaper_information(uid: str):
    wallpaper = get_single_wallpaper(uid)
    if type(wallpaper) == tuple:
        return wallpaper
    return wallpaper_mapper(wallpaper, extended=True)

@app.patch("/api/user/set")
def set_user():
    if not request.json.get("token") or not request.json.get("wallpaper_uid"):
        return json.dumps({
            "error": "token and wallpaper_uid are required"
        }), 400

    result, error = jwt_authentik.set_user_wallpaper(request.json.get("token"),
                                                     request.json.get("wallpaper_uid"))
    if not result:
        return json.dumps({
            "error": error
        }), 400

    return {
        "ok": True
    }, 200
