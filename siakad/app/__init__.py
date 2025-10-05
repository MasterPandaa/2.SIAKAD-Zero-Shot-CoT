import os
from flask import Flask
from .config import Config
from .extensions import db, login_manager


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from .blueprints.auth.routes import auth_bp
    from .blueprints.main.routes import main_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(main_bp)

    # Defer import of other blueprints until their files exist
    try:
        from .blueprints.students.routes import students_bp
        from .blueprints.teachers.routes import teachers_bp
        from .blueprints.subjects.routes import subjects_bp
        from .blueprints.grades.routes import grades_bp
        app.register_blueprint(students_bp, url_prefix="/students")
        app.register_blueprint(teachers_bp, url_prefix="/teachers")
        app.register_blueprint(subjects_bp, url_prefix="/subjects")
        app.register_blueprint(grades_bp, url_prefix="/grades")
    except Exception:
        # Blueprints might not exist yet during first run
        pass

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None

    # Auto-create tables (for quick start). For production, prefer migrations/SQL schema.
    with app.app_context():
        try:
            from . import models  # ensure models are imported
            db.create_all()
        except Exception:
            pass

    return app
