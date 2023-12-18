import boto3
from flask import Blueprint, jsonify, url_for
from backend.database.redis import WallpaperStatus, get_all_wallpapers, remove_single_wallpaper
from backend.config import AppConfig
from backend.worker.image_processor import handle_all_images, celery
from celery.result import AsyncResult
from celery.app.control import Inspect

tasks = Blueprint("tasks", __name__, template_folder="templates")

s3_results = boto3.client('s3',
                          endpoint_url=AppConfig.RESULT.S3_URL,
                          config=boto3.session.Config(signature_version='s3v4'),
                          aws_access_key_id=AppConfig.RESULT.S3_ACCESS_KEY,
                          aws_secret_access_key=AppConfig.RESULT.S3_SECRET_KEY,
                          )


@tasks.route("/", methods=["GET"])
def taskreports():
    tasks: Inspect = celery.control.inspect()

    return jsonify(
        {
            "scheduled": tasks.scheduled(),
            "active": tasks.active(),
            "reserved": tasks.reserved(),
        }
    )


@tasks.route("/status/<task_id>", methods=["GET"])
def single_task_status(task_id):
    task = handle_all_images.AsyncResult(task_id)
    if task.state == "PENDING":
        response = {
            "queue_state": task.state,
            "status": task.info,
            "status_update": url_for("tasks.single_task_status", task_id=task.id),
        }
    else:
        response = {"queue_state": task.state, "result": task.wait()}
    return jsonify(response)


@tasks.route("/status/<task_id>", methods=["DELETE"])
def revoke_task(task_id):
    task: AsyncResult = handle_all_images.AsyncResult(task_id)

    if task.state == "PENDING":
        task.revoke(terminate=True)
        response = {
            "queue_state": task.state,
            "status": task.info,
            "status_update": url_for("tasks.single_task_status", task_id=task.id),
        }
    else:
        response = {"queue_state": task.state, "result": task.wait()}
    return jsonify(response)


def amount_of_pending_tasks():
    tasks: Inspect = celery.control.inspect()

    total_active_tasks = 0
    sch = tasks.scheduled()
    total_active_tasks += sum([len(i) for i in sch.values()]) if sch else 0
    sch = tasks.active()
    total_active_tasks += sum([len(i) for i in sch.values()]) if sch else 0
    sch = tasks.reserved()
    total_active_tasks += sum([len(i) for i in sch.values()]) if sch else 0
    return total_active_tasks


@tasks.route("/gc")
def garbage_collect():
    if amount_of_pending_tasks() > 0:
        return "There are still tasks pending", 400

    print("Going to garbage collect")

    all_wallpapers = get_all_wallpapers()
    removed = 0
    for wall in all_wallpapers:
        if not wall["status"] == WallpaperStatus.READY:
            print("This wallpaper errored somewhere:", wall)

            all_files = s3_results.list_objects_v2(Bucket=AppConfig.RESULT.BUCKET,
                                                   Prefix=f"{wall['uid']}/")
            if not all_files["KeyCount"] == 0:
                for file in all_files["Contents"]:
                    print("Removing file:", file)
                    s3_results.delete_object(Bucket=AppConfig.RESULT.BUCKET,
                                             Key=file["Key"])

            remove_single_wallpaper(wall["uid"])
            removed += 1
    return f"Removed {removed} folders", 200
