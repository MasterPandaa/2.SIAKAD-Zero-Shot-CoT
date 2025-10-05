from app.extensions import db
from app.models import User
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("main.dashboard"))
        flash("Username atau password salah", "danger")
    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth_bp.route("/init")
def init_admin():
    # Create initial admin if none exists
    if User.query.filter_by(role="admin").first():
        flash("Admin sudah ada. Rute init dinonaktifkan.", "info")
        return redirect(url_for("auth.login"))
    admin = User(username="admin", role="admin")
    admin.set_password("admin123")
    db.session.add(admin)
    db.session.commit()
    flash(
        "Admin dibuat. Username: admin, Password: admin123. Harap ganti setelah login.",
        "success",
    )
    return redirect(url_for("auth.login"))
