from datetime import date

from app.extensions import db
from app.models import Student, User
from app.utils import role_required
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

students_bp = Blueprint("students", __name__)


@students_bp.route("/")
@role_required("admin", "teacher")
def index():
    # Admin and Teacher can list students; Student can only view their own via detail
    students = Student.query.order_by(Student.class_name, Student.name).all()
    return render_template("students/index.html", students=students)


@students_bp.route("/create", methods=["GET", "POST"])
@role_required("admin")
def create():
    if request.method == "POST":
        try:
            nis = request.form.get("nis", "").strip()
            name = request.form.get("name", "").strip()
            birth_date_str = request.form.get("birth_date", "").strip()
            address = request.form.get("address", "").strip()
            gender = request.form.get("gender", "L").strip()
            parent_phone = request.form.get("parent_phone", "").strip()
            class_name = request.form.get("class_name", "").strip()

            bdate = date.fromisoformat(birth_date_str)
            s = Student(
                nis=nis,
                name=name,
                birth_date=bdate,
                address=address,
                gender=gender,
                parent_phone=parent_phone,
                class_name=class_name,
            )
            db.session.add(s)
            db.session.flush()

            if request.form.get("create_login") == "on":
                username = request.form.get("username", "").strip()
                password = request.form.get("password", "")
                if username and password:
                    u = User(username=username,
                             role="student", student_id=s.id)
                    u.set_password(password)
                    db.session.add(u)
                else:
                    flash("Username dan password wajib jika membuat login.", "warning")

            db.session.commit()
            flash("Siswa berhasil ditambahkan.", "success")
            return redirect(url_for("students.index"))
        except Exception as e:
            db.session.rollback()
            flash(f"Gagal menambah siswa: {e}", "danger")
    return render_template("students/create.html")


@students_bp.route("/<int:student_id>")
@login_required
def detail(student_id):
    s = Student.query.get_or_404(student_id)
    if current_user.role == "student" and current_user.student_id != s.id:
        abort(403)
    return render_template("students/detail.html", s=s)


@students_bp.route("/<int:student_id>/edit", methods=["GET", "POST"])
@role_required("admin")
def edit(student_id):
    s = Student.query.get_or_404(student_id)
    if request.method == "POST":
        try:
            s.nis = request.form.get("nis", s.nis).strip()
            s.name = request.form.get("name", s.name).strip()
            birth_date_str = request.form.get(
                "birth_date", s.birth_date.isoformat()
            ).strip()
            s.birth_date = date.fromisoformat(birth_date_str)
            s.address = request.form.get("address", s.address or "").strip()
            s.gender = request.form.get("gender", s.gender).strip()
            s.parent_phone = request.form.get(
                "parent_phone", s.parent_phone or ""
            ).strip()
            s.class_name = request.form.get("class_name", s.class_name).strip()
            db.session.commit()
            flash("Siswa berhasil diperbarui.", "success")
            return redirect(url_for("students.index"))
        except Exception as e:
            db.session.rollback()
            flash(f"Gagal memperbarui siswa: {e}", "danger")
    return render_template("students/edit.html", s=s)


@students_bp.route("/<int:student_id>/delete")
@role_required("admin")
def delete(student_id):
    s = Student.query.get_or_404(student_id)
    try:
        # Delete linked user if exists
        u = User.query.filter_by(student_id=s.id).first()
        if u:
            db.session.delete(u)
        db.session.delete(s)
        db.session.commit()
        flash("Siswa berhasil dihapus.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Gagal menghapus siswa: {e}", "danger")
    return redirect(url_for("students.index"))
