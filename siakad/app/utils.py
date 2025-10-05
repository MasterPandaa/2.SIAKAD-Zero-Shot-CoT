from functools import wraps
from flask import abort
from flask_login import current_user, login_required


def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        @login_required
        def wrapper(*args, **kwargs):
            if current_user.role not in roles:
                abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def calc_final(tugas, uts, uas) -> float:
    try:
        t = float(tugas)
        u1 = float(uts)
        u2 = float(uas)
        return round((t + u1 + u2) / 3.0, 2)
    except Exception:
        return 0.0
