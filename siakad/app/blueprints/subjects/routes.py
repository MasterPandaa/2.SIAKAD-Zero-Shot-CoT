from app.extensions import db
from app.models import Subject, Teacher
from app.utils import role_required
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

subjects_bp = Blueprint("subjects", __name__)


@subjects_bp.route("/")
@role_required("admin", "teacher")
def index():
    q = Subject.query
    if current_user.role == "teacher" and current_user.teacher_id:
        q = q.filter(Subject.teacher_id == current_user.teacher_id)
    subjects = q.order_by(Subject.code).all()
    return render_template("subjects/index.html", subjects=subjects)


@subjects_bp.route("/create", methods=["GET", "POST"])
@role_required("admin")
def create():
    teachers = Teacher.query.order_by(Teacher.name).all()
    if request.method == "POST":
        try:
            code = request.form.get("code", "").strip()
            name = request.form.get("name", "").strip()
            sks = int(request.form.get("sks", 2))
            teacher_id = request.form.get("teacher_id")
            teacher_id = int(teacher_id) if teacher_id else None

            s = Subject(code=code, name=name, sks=sks, teacher_id=teacher_id)
            db.session.add(s)
            db.session.commit()
            flash("Mata pelajaran berhasil ditambahkan.", "success")
            return redirect(url_for("subjects.index"))
        except Exception as e:
            db.session.rollback()
            flash(f"Gagal menambah mata pelajaran: {e}", "danger")
    return render_template("subjects/create.html", teachers=teachers)


@subjects_bp.route("/<int:subject_id>/edit", methods=["GET", "POST"])
@role_required("admin")
def edit(subject_id):
    subj = Subject.query.get_or_404(subject_id)
    teachers = Teacher.query.order_by(Teacher.name).all()
    if request.method == "POST":
        try:
            subj.code = request.form.get("code", subj.code).strip()
            subj.name = request.form.get("name", subj.name).strip()
            subj.sks = int(request.form.get("sks", subj.sks))
            teacher_id = request.form.get("teacher_id")
            subj.teacher_id = int(teacher_id) if teacher_id else None
            db.session.commit()
            flash("Mata pelajaran berhasil diperbarui.", "success")
            return redirect(url_for("subjects.index"))
        except Exception as e:
            db.session.rollback()
            flash(f"Gagal memperbarui mata pelajaran: {e}", "danger")
    return render_template("subjects/edit.html", subj=subj, teachers=teachers)


@subjects_bp.route("/<int:subject_id>/delete")
@role_required("admin")
def delete(subject_id):
    subj = Subject.query.get_or_404(subject_id)
    try:
        db.session.delete(subj)
        db.session.commit()
        flash("Mata pelajaran berhasil dihapus.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Gagal menghapus mata pelajaran: {e}", "danger")
    return redirect(url_for("subjects.index"))
