from datetime import datetime
import os
from uuid import uuid4
from flask import Flask, jsonify, request, url_for
from config import AppConfig
from workers.image_processor import func1, handle_image
import heic
import pyheif
from PIL import Image
from tasks import tasks

ALLOWED_EXTENSIONS = {"heic", "png", "jpg", "jpeg", "gif"}


def get_extension(filename):
    return filename.rsplit(".", 1)[1].lower()


def allowed_file(filename):
    return "." in filename and get_extension(filename) in ALLOWED_EXTENSIONS


app = Flask(__name__)
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
        task = handle_image.delay(new_filename)
        return jsonify(
            {"taskid": url_for("tasks.taskstatus", task_id=task.id), "ok": True}
        )
    return "This is not a valid extension", 400


@app.route("/wallpapers")
def get_wallpapers():
    # Returns a list of all available .heic wallpapers with identifiers?
    wallpapers = [
        f.name
        for f in os.scandir("wallpapers")
        if f.is_file() and f.name.endswith(".heic")
    ]
    return jsonify(wallpapers)


@app.route("/wallpaper/<string:name>")
def get_wallpaper(name: str):
    starttime = datetime.now()
    print(name)
    if not name.endswith(".heic"):
        # special logic?
        assert False

    c = heic.get_wallpaper_config(f"wallpapers/{name}")
    print(c)
    # TODO: Do this check on upload
    if "si" in c:
        print("Sun based wallpapers are not yet supported.", file=sys.stderr)
        sys.exit(1)

    times = c["ti"]
    times.sort(key=lambda x: x["t"])
    prev = -0.1
    for d in times:
        cur = float(d["t"])
        if not 0.0 <= cur <= 1.0:
            print("Warning: Invalid time specification found. Might skip some images.")
        if cur == prev:
            print("Warning: Ambigous time specifiation found. Might skip some images.")
        prev = cur

    times = c["ti"]
    times.sort(key=lambda x: x["t"])
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

    heif_container = pyheif.open_container(f"wallpapers/{name}")
    all_images = heif_container.top_level_images

    assert index < len(all_images)

    heif_file = all_images[index].image

    heif_file.load()
    print(heif_file)
    img = Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw",
        heif_file.mode,
        heif_file.stride,
    )

    img.thumbnail((3000, 3000))
    img.save("test.png", quality=85, optimize=True)

    # print()

    return jsonify(index, (datetime.now() - starttime).microseconds // 1000)
    # Returns a URL (which nginx? should serve) for a specific name and a specific time
