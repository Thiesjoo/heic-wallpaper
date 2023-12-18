import json
from datetime import datetime
import time
from uuid import uuid4

import boto3
from flask import Flask, request, url_for, redirect, jsonify
from werkzeug.utils import secure_filename

from backend.config import AppConfig
from backend.database.redis import WallpaperType, add_wallpaper, WallpaperStatus, \
    Wallpaper, get_single_wallpaper, update_status_of_wallpaper, get_all_wallpapers

app = Flask(
    __name__,
)

s3 = boto3.client('s3',
                  endpoint_url=AppConfig.UPLOAD.S3_URL,
                  config=boto3.session.Config(signature_version='s3v4'),
                  aws_access_key_id=AppConfig.UPLOAD.S3_ACCESS_KEY,
                  aws_secret_access_key=AppConfig.UPLOAD.S3_SECRET_KEY,
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


@app.route("/api/upload", methods=["POST"])
def upload():
    file_name = request.json.get('name')

    file_type = request.json.get('type')
    print(file_type, file_name)
    if file_name is None or file_type is None:
        return json.dumps({
            'error': 'name and type are required'
        }), 400

    uid = str(uuid4())
    new_filename = f"{uid}.{get_extension(file_name)}"

    presigned_post = s3.generate_presigned_post(
        Bucket=AppConfig.UPLOAD_S3_BUCKET,
        Key=new_filename,
        Fields={"acl": "public-read", "Content-Type": file_type},
        Conditions=[
            {"acl": "public-read"},
            {"Content-Type": file_type}
        ],
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
            "type": detemine_type_from_extension(get_extension(file_name)),
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
    print("Req for:", uid, key)

    try:
        s3.head_object(Bucket=AppConfig.UPLOAD_S3_BUCKET, Key=key)
    except Exception as e:
        print(e)
        return json.dumps({
            'error': 'invalid uid/key'
        }), 400

    update_status_of_wallpaper(uid, WallpaperStatus.PROCESSING)
    print("Starting task")

    return json.dumps({
        'data': 'ok'
    }), 202

def wallpaper_mapper(wallpaper: Wallpaper, extended=False):
    to_return = {
        "name": wallpaper["original_name"],
        "id": wallpaper["uid"],
        "created_by": wallpaper[
            "created_by"] if "created_by" in wallpaper else "Unknown",
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
