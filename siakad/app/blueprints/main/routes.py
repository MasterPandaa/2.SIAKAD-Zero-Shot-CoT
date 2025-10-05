from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func
from app.extensions import db
from app.models import Student, Teacher, Subject, Grade

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@login_required
def dashboard():
    students_count = db.session.query(func.count(Student.id)).scalar() or 0
    teachers_count = db.session.query(func.count(Teacher.id)).scalar() or 0
    subjects_count = db.session.query(func.count(Subject.id)).scalar() or 0

    results = (
        db.session.query(Subject.name, func.avg(Grade.final_score))
        .join(Grade, Grade.subject_id == Subject.id)
        .group_by(Subject.name)
        .all()
    )

    labels = [r[0] for r in results]
    data = [round(r[1], 2) if r[1] is not None else 0 for r in results]

    return render_template(
        "dashboard.html",
        students_count=students_count,
        teachers_count=teachers_count,
        subjects_count=subjects_count,
        chart_labels=labels,
        chart_data=data,
    )
