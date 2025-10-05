from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from sqlalchemy import func
from app.extensions import db
from app.models import Student, Teacher, Subject, Grade
from app.utils import role_required, calc_final

grades_bp = Blueprint("grades", __name__)


def _subjects_for_user():
    q = Subject.query
    if current_user.role == "teacher" and current_user.teacher_id:
        q = q.filter(Subject.teacher_id == current_user.teacher_id)
    return q.order_by(Subject.name).all()


def _classes():
    rows = db.session.query(Student.class_name).distinct().order_by(Student.class_name).all()
    return [r[0] for r in rows]


@grades_bp.route("/select", methods=["GET", "POST"])
@role_required("admin", "teacher")
def select_input():
    subjects = _subjects_for_user()
    classes = _classes()
    if request.method == "POST":
        subject_id = request.form.get("subject_id")
        class_name = request.form.get("class_name")
        if not subject_id or not class_name:
            flash("Pilih mata pelajaran dan kelas.", "warning")
            return redirect(url_for("grades.select_input"))
        return redirect(url_for("grades.input_scores", subject_id=subject_id, class_name=class_name))
    return render_template("grades/select_input.html", subjects=subjects, classes=classes)


@grades_bp.route("/input")
@role_required("admin", "teacher")
def input_scores():
    subject_id = request.args.get("subject_id", type=int)
    class_name = request.args.get("class_name", type=str)
    subj = Subject.query.get_or_404(subject_id)
    if current_user.role == "teacher" and subj.teacher_id != current_user.teacher_id:
        abort(403)

    students = Student.query.filter_by(class_name=class_name).order_by(Student.name).all()
    grades = Grade.query.filter_by(subject_id=subject_id).all()
    by_student = {g.student_id: g for g in grades}

    return render_template(
        "grades/input.html",
        subj=subj,
        class_name=class_name,
        students=students,
        grades_by_student=by_student,
    )


@grades_bp.route("/input", methods=["POST"])
@role_required("admin", "teacher")
def save_scores():
    subject_id = request.args.get("subject_id", type=int)
    class_name = request.args.get("class_name", type=str)
    subj = Subject.query.get_or_404(subject_id)
    if current_user.role == "teacher" and subj.teacher_id != current_user.teacher_id:
        abort(403)

    students = Student.query.filter_by(class_name=class_name).all()
    try:
        for s in students:
            tugas = float(request.form.get(f"tugas_{s.id}", 0) or 0)
            uts = float(request.form.get(f"uts_{s.id}", 0) or 0)
            uas = float(request.form.get(f"uas_{s.id}", 0) or 0)
            final = calc_final(tugas, uts, uas)

            g = Grade.query.filter_by(student_id=s.id, subject_id=subject_id).first()
            if not g:
                g = Grade(student_id=s.id, subject_id=subject_id)
                db.session.add(g)
            g.tugas = tugas
            g.uts = uts
            g.uas = uas
            g.final_score = final
        db.session.commit()
        flash("Nilai berhasil disimpan.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Gagal menyimpan nilai: {e}", "danger")

    return redirect(url_for("grades.input_scores", subject_id=subject_id, class_name=class_name))


@grades_bp.route("/transcript")
@login_required
def transcript():
    # Determine which student's transcript to view
    students = None
    target_student = None
    if current_user.role == "student" and current_user.student_id:
        target_student = Student.query.get(current_user.student_id)
    else:
        students = Student.query.order_by(Student.class_name, Student.name).all()
        student_id = request.args.get("student_id", type=int)
        if student_id:
            target_student = Student.query.get_or_404(student_id)

    grades = []
    if target_student:
        query = (
            db.session.query(
                Subject.code,
                Subject.name,
                Subject.sks,
                Grade.tugas,
                Grade.uts,
                Grade.uas,
                Grade.final_score,
            )
            .join(Grade, Grade.subject_id == Subject.id)
            .filter(Grade.student_id == target_student.id)
        )
        if current_user.role == "teacher" and current_user.teacher_id:
            query = query.filter(Subject.teacher_id == current_user.teacher_id)
        grades = query.order_by(Subject.code).all()

    return render_template("grades/transcript.html", target_student=target_student, students=students, grades=grades)


@grades_bp.route("/report", methods=["GET", "POST"])
@role_required("admin", "teacher")
def report_select():
    subjects = _subjects_for_user()
    classes = _classes()
    if request.method == "POST":
        subject_id = request.form.get("subject_id")
        class_name = request.form.get("class_name")
        if not subject_id or not class_name:
            flash("Pilih mata pelajaran dan kelas.", "warning")
            return redirect(url_for("grades.report_select"))
        return redirect(url_for("grades.report_print", subject_id=subject_id, class_name=class_name))
    return render_template("grades/report_select.html", subjects=subjects, classes=classes)


@grades_bp.route("/report/print")
@role_required("admin", "teacher")
def report_print():
    subject_id = request.args.get("subject_id", type=int)
    class_name = request.args.get("class_name", type=str)
    subj = Subject.query.get_or_404(subject_id)
    if current_user.role == "teacher" and subj.teacher_id != current_user.teacher_id:
        abort(403)

    students = Student.query.filter_by(class_name=class_name).order_by(Student.name).all()
    grades = Grade.query.filter_by(subject_id=subject_id).all()
    by_student = {g.student_id: g for g in grades}

    return render_template(
        "grades/report_print.html",
        subj=subj,
        class_name=class_name,
        students=students,
        grades_by_student=by_student,
    )
