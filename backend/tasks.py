import os
import shutil
from flask import Blueprint, jsonify, url_for
from backend.database.redis import WallpaperStatus, get_all_wallpapers, remove_single_wallpaper
from backend.config import AppConfig
from backend.worker.image_processor import handle_image, celery
from celery.result import AsyncResult
from celery.app.control import Inspect

tasks = Blueprint("tasks", __name__, template_folder="templates")


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
    task = handle_image.AsyncResult(task_id)
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
    task: AsyncResult = handle_image.AsyncResult(task_id)

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

    shutil.rmtree(f"{AppConfig.UPLOAD_FOLDER}/")
    os.mkdir(f"{AppConfig.UPLOAD_FOLDER}/")

    all_wallpapers = get_all_wallpapers()
    removed = 0
    for wall in all_wallpapers:
        if not wall["status"] == WallpaperStatus.READY:
            print("This wallpaper errored somewhere:", wall)
            shutil.rmtree(
                f"{AppConfig.PROCESSED_FOLDER}/{wall['uuid']}", ignore_errors=True
            )
            remove_single_wallpaper(wall["uuid"])
            removed += 1
    return f"Removed {removed} folders", 200
