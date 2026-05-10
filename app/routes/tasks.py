from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app import db, socketio
from app.models import Task

tasks_bp = Blueprint("tasks", __name__)


def emit_task_update(event, task_data, user_id):
    """Emit a WebSocket event for real-time updates."""
    socketio.emit(event, {"task": task_data, "user_id": user_id}, room=f"user_{user_id}")


@tasks_bp.route("/", methods=["GET"])
@login_required
def get_tasks():
    """Get all tasks for the current user with optional filters."""
    status = request.args.get("status")
    priority = request.args.get("priority")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    query = Task.query.filter_by(user_id=current_user.id)

    if status and status in Task.VALID_STATUSES:
        query = query.filter_by(status=status)
    if priority and priority in Task.VALID_PRIORITIES:
        query = query.filter_by(priority=priority)

    query = query.order_by(Task.created_at.desc())
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "success": True,
        "tasks": [task.to_dict() for task in paginated.items],
        "total": paginated.total,
        "pages": paginated.pages,
        "current_page": page,
    })


@tasks_bp.route("/<int:task_id>", methods=["GET"])
@login_required
def get_task(task_id):
    """Get a single task by ID."""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    return jsonify({"success": True, "task": task.to_dict()})


@tasks_bp.route("/", methods=["POST"])
@login_required
def add_task():
    """Create a new task."""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data provided."}), 400

    title = data.get("title", "").strip()
    if not title:
        return jsonify({"success": False, "message": "Title is required."}), 400

    priority = data.get("priority", "medium").lower()
    if priority not in Task.VALID_PRIORITIES:
        return jsonify({"success": False, "message": f"Priority must be one of: {', '.join(Task.VALID_PRIORITIES)}"}), 400

    status = data.get("status", "pending").lower()
    if status not in Task.VALID_STATUSES:
        return jsonify({"success": False, "message": f"Status must be one of: {', '.join(Task.VALID_STATUSES)}"}), 400

    due_date = None
    if data.get("due_date"):
        try:
            due_date = datetime.fromisoformat(data["due_date"])
        except ValueError:
            return jsonify({"success": False, "message": "Invalid due_date format. Use ISO 8601."}), 400

    task = Task(
        title=title,
        description=data.get("description", "").strip(),
        priority=priority,
        status=status,
        due_date=due_date,
        user_id=current_user.id,
    )
    db.session.add(task)
    db.session.commit()

    emit_task_update("task_created", task.to_dict(), current_user.id)

    return jsonify({"success": True, "message": "Task created.", "task": task.to_dict()}), 201


@tasks_bp.route("/<int:task_id>", methods=["PUT"])
@login_required
def update_task(task_id):
    """Update an existing task."""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data provided."}), 400

    if "title" in data:
        title = data["title"].strip()
        if not title:
            return jsonify({"success": False, "message": "Title cannot be empty."}), 400
        task.title = title

    if "description" in data:
        task.description = data["description"].strip()

    if "priority" in data:
        priority = data["priority"].lower()
        if priority not in Task.VALID_PRIORITIES:
            return jsonify({"success": False, "message": f"Priority must be one of: {', '.join(Task.VALID_PRIORITIES)}"}), 400
        task.priority = priority

    if "status" in data:
        status = data["status"].lower()
        if status not in Task.VALID_STATUSES:
            return jsonify({"success": False, "message": f"Status must be one of: {', '.join(Task.VALID_STATUSES)}"}), 400
        task.status = status

    if "due_date" in data:
        if data["due_date"]:
            try:
                task.due_date = datetime.fromisoformat(data["due_date"])
            except ValueError:
                return jsonify({"success": False, "message": "Invalid due_date format."}), 400
        else:
            task.due_date = None

    task.updated_at = datetime.utcnow()
    db.session.commit()

    emit_task_update("task_updated", task.to_dict(), current_user.id)

    return jsonify({"success": True, "message": "Task updated.", "task": task.to_dict()})


@tasks_bp.route("/<int:task_id>", methods=["DELETE"])
@login_required
def delete_task(task_id):
    """Delete a task."""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    task_data = task.to_dict()
    db.session.delete(task)
    db.session.commit()

    emit_task_update("task_deleted", task_data, current_user.id)

    return jsonify({"success": True, "message": "Task deleted."})
