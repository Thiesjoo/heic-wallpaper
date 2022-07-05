from flask import Blueprint, jsonify, url_for
from workers.image_processor import handle_image, celery
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
        task.revoke()
        response = {
            "queue_state": task.state,
            "status": task.info,
            "status_update": url_for("tasks.single_task_status", task_id=task.id),
        }
    else:
        response = {"queue_state": task.state, "result": task.wait()}
    return jsonify(response)
