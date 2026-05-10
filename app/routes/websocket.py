from flask import request
from flask_login import current_user
from flask_socketio import join_room, leave_room, emit


def register_socketio_events(socketio):
    """Register all SocketIO event handlers."""

    @socketio.on("connect")
    def on_connect():
        if current_user.is_authenticated:
            room = f"user_{current_user.id}"
            join_room(room)
            emit("connected", {
                "message": f"Connected to real-time updates.",
                "user_id": current_user.id,
                "room": room,
            })
        else:
            return False  # Reject unauthenticated connections

    @socketio.on("disconnect")
    def on_disconnect():
        if current_user.is_authenticated:
            room = f"user_{current_user.id}"
            leave_room(room)

    @socketio.on("join")
    def on_join(data):
        if current_user.is_authenticated:
            room = f"user_{current_user.id}"
            join_room(room)
            emit("joined", {"room": room})

    @socketio.on("ping_server")
    def on_ping():
        emit("pong_server", {"message": "Server is alive."})
