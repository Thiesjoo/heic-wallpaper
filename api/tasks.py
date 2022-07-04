from flask import Blueprint, jsonify, url_for
from workers.image_processor import func1

tasks = Blueprint("tasks", __name__, template_folder="templates")


@tasks.route("/status/<task_id>")
def taskstatus(task_id):
    task = func1.AsyncResult(task_id)
    if task.state == "PENDING":
        response = {
            "queue_state": task.state,
            "status": task.info,
            "status_update": url_for("tasks.taskstatus", task_id=task.id),
        }
    else:
        response = {"queue_state": task.state, "result": task.wait()}
    return jsonify(response)
