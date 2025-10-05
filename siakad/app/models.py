from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from .extensions import db


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin | teacher | student
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"), nullable=True)

    student = db.relationship("Student", backref=db.backref("user", uselist=False))
    teacher = db.relationship("Teacher", backref=db.backref("user", uselist=False))

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    nis = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    address = db.Column(db.Text, nullable=True)
    gender = db.Column(db.String(1), nullable=False)  # L/P
    parent_phone = db.Column(db.String(20), nullable=True)
    class_name = db.Column(db.String(20), nullable=False)

    grades = db.relationship("Grade", backref="student", cascade="all, delete-orphan")


class Teacher(db.Model):
    __tablename__ = "teachers"
    id = db.Column(db.Integer, primary_key=True)
    nip = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)

    subjects = db.relationship("Subject", backref="teacher", cascade="all, delete-orphan")


class Subject(db.Model):
    __tablename__ = "subjects"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    sks = db.Column(db.Integer, nullable=False, default=2)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"), nullable=True)

    grades = db.relationship("Grade", backref="subject", cascade="all, delete-orphan")


class Grade(db.Model):
    __tablename__ = "grades"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)
    tugas = db.Column(db.Float, nullable=False, default=0)
    uts = db.Column(db.Float, nullable=False, default=0)
    uas = db.Column(db.Float, nullable=False, default=0)
    final_score = db.Column(db.Float, nullable=False, default=0)

    __table_args__ = (
        db.UniqueConstraint("student_id", "subject_id", name="uq_grade_student_subject"),
    )
