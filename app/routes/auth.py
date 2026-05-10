from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        data = request.get_json() if request.is_json else request.form
        username = data.get("username", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        errors = {}
        if not username or len(username) < 3:
            errors["username"] = "Username must be at least 3 characters."
        if not email or "@" not in email:
            errors["email"] = "Valid email is required."
        if not password or len(password) < 6:
            errors["password"] = "Password must be at least 6 characters."
        if User.query.filter_by(username=username).first():
            errors["username"] = "Username already taken."
        if User.query.filter_by(email=email).first():
            errors["email"] = "Email already registered."

        if errors:
            if request.is_json:
                return jsonify({"success": False, "errors": errors}), 400
            for field, msg in errors.items():
                flash(msg, "danger")
            return render_template("auth/register.html")

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        if request.is_json:
            return jsonify({"success": True, "message": "Registration successful."}), 201
        flash("Account created! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        data = request.get_json() if request.is_json else request.form
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        remember = data.get("remember", False)

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=bool(remember))
            if request.is_json:
                return jsonify({"success": True, "message": "Login successful.", "user": user.to_dict()})
            return redirect(url_for("main.dashboard"))

        if request.is_json:
            return jsonify({"success": False, "message": "Invalid email or password."}), 401
        flash("Invalid email or password.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/me")
@login_required
def me():
    return jsonify({"success": True, "user": current_user.to_dict()})
