from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.models import Teacher, User
from app.utils import role_required

teachers_bp = Blueprint("teachers", __name__)


@teachers_bp.route("/")
@role_required("admin")
def index():
    teachers = Teacher.query.order_by(Teacher.name).all()
    return render_template("teachers/index.html", teachers=teachers)


@teachers_bp.route("/create", methods=["GET", "POST"])
@role_required("admin")
def create():
    if request.method == "POST":
        try:
            nip = request.form.get("nip", "").strip()
            name = request.form.get("name", "").strip()
            phone = request.form.get("phone", "").strip()
            address = request.form.get("address", "").strip()
            t = Teacher(nip=nip, name=name, phone=phone, address=address)
            db.session.add(t)
            db.session.flush()

            if request.form.get("create_login") == "on":
                username = request.form.get("username", "").strip()
                password = request.form.get("password", "")
                if username and password:
                    u = User(username=username, role="teacher", teacher_id=t.id)
                    u.set_password(password)
                    db.session.add(u)
                else:
                    flash("Username dan password wajib jika membuat login.", "warning")

            db.session.commit()
            flash("Guru berhasil ditambahkan.", "success")
            return redirect(url_for("teachers.index"))
        except Exception as e:
            db.session.rollback()
            flash(f"Gagal menambah guru: {e}", "danger")
    return render_template("teachers/create.html")


@teachers_bp.route("/<int:teacher_id>/edit", methods=["GET", "POST"])
@role_required("admin")
def edit(teacher_id):
    t = Teacher.query.get_or_404(teacher_id)
    if request.method == "POST":
        try:
            t.nip = request.form.get("nip", t.nip).strip()
            t.name = request.form.get("name", t.name).strip()
            t.phone = request.form.get("phone", t.phone or "").strip()
            t.address = request.form.get("address", t.address or "").strip()
            db.session.commit()
            flash("Guru berhasil diperbarui.", "success")
            return redirect(url_for("teachers.index"))
        except Exception as e:
            db.session.rollback()
            flash(f"Gagal memperbarui guru: {e}", "danger")
    return render_template("teachers/edit.html", t=t)


@teachers_bp.route("/<int:teacher_id>/delete")
@role_required("admin")
def delete(teacher_id):
    t = Teacher.query.get_or_404(teacher_id)
    try:
        u = User.query.filter_by(teacher_id=t.id).first()
        if u:
            db.session.delete(u)
        db.session.delete(t)
        db.session.commit()
        flash("Guru berhasil dihapus.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Gagal menghapus guru: {e}", "danger")
    return redirect(url_for("teachers.index"))
