from datetime import datetime
import os
from flask import Flask, jsonify
import heic
import pyheif
from PIL import Image

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


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
