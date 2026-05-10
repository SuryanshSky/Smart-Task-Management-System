from flask import Blueprint, jsonify
from flask_login import login_required, current_user
import pandas as pd
import numpy as np
from app.models import Task

analytics_bp = Blueprint("analytics", __name__)


def get_user_tasks_df(user_id):
    """Fetch user tasks and return as a Pandas DataFrame."""
    tasks = Task.query.filter_by(user_id=user_id).all()
    if not tasks:
        return pd.DataFrame(columns=["id", "title", "priority", "status", "created_at", "updated_at"])
    records = [t.to_dict() for t in tasks]
    df = pd.DataFrame(records)
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["updated_at"] = pd.to_datetime(df["updated_at"], errors="coerce")
    return df


@analytics_bp.route("/summary", methods=["GET"])
@login_required
def summary():
    """Return analytics summary using Pandas & NumPy."""
    df = get_user_tasks_df(current_user.id)

    if df.empty:
        return jsonify({
            "success": True,
            "analytics": {
                "total_tasks": 0,
                "completed_tasks": 0,
                "pending_tasks": 0,
                "in_progress_tasks": 0,
                "completion_percentage": 0.0,
                "priority_breakdown": {"low": 0, "medium": 0, "high": 0},
                "status_breakdown": {"pending": 0, "in_progress": 0, "completed": 0},
                "avg_tasks_per_day": 0.0,
                "tasks_this_week": 0,
                "completion_trend": [],
            }
        })

    total = len(df)
    status_counts = df["status"].value_counts().to_dict()
    priority_counts = df["priority"].value_counts().to_dict()

    completed = int(status_counts.get("completed", 0))
    pending = int(status_counts.get("pending", 0))
    in_progress = int(status_counts.get("in_progress", 0))

    # NumPy for completion percentage
    completion_pct = float(np.round((completed / total) * 100, 2)) if total > 0 else 0.0

    # Tasks created this week
    now = pd.Timestamp.utcnow().tz_localize(None)
    week_ago = now - pd.Timedelta(days=7)
    created_at_naive = df["created_at"].dt.tz_localize(None) if df["created_at"].dt.tz is not None else df["created_at"]
    tasks_this_week = int((created_at_naive >= week_ago).sum())

    # Average tasks per day
    if len(df) > 1:
        date_range_days = max((created_at_naive.max() - created_at_naive.min()).days, 1)
        avg_per_day = float(np.round(total / date_range_days, 2))
    else:
        avg_per_day = float(total)

    # Daily completion trend (last 7 days)
    trend = []
    for i in range(6, -1, -1):
        day = now - pd.Timedelta(days=i)
        day_label = day.strftime("%a")
        mask = (
            (df["status"] == "completed") &
            (created_at_naive.dt.date == day.date())
        )
        trend.append({"day": day_label, "count": int(mask.sum())})

    # Priority distribution using numpy
    priority_array = df["priority"].values
    unique_priorities, priority_freq = np.unique(priority_array, return_counts=True)
    priority_breakdown = {p: int(c) for p, c in zip(unique_priorities, priority_freq)}
    for p in ["low", "medium", "high"]:
        priority_breakdown.setdefault(p, 0)

    status_breakdown = {
        "pending": pending,
        "in_progress": in_progress,
        "completed": completed,
    }

    return jsonify({
        "success": True,
        "analytics": {
            "total_tasks": total,
            "completed_tasks": completed,
            "pending_tasks": pending,
            "in_progress_tasks": in_progress,
            "completion_percentage": completion_pct,
            "priority_breakdown": priority_breakdown,
            "status_breakdown": status_breakdown,
            "avg_tasks_per_day": avg_per_day,
            "tasks_this_week": tasks_this_week,
            "completion_trend": trend,
        }
    })
