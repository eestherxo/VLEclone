from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.user_service import get_user
from app.services.reports_service import *

report_bp = Blueprint("report", __name__, url_prefix="/report")


def _require_admin(user_id):
    user = get_user(user_id)
    if not user or user["role"].lower() != "admin":
        return None, {"error": "Only admins can view reports"}, 403
    return user, None, None


@report_bp.get("/courses/popular")
@jwt_required()
def popular_courses():
    user, err, code = _require_admin(get_jwt_identity())
    if err:
        return err, code
    try:
        return {"courses": get_popular_courses()}, 200
    except Exception as e:
        return {"error": str(e)}, 400


@report_bp.get("/students/busy")
@jwt_required()
def busy_students():
    user, err, code = _require_admin(get_jwt_identity())
    if err:
        return err, code
    try:
        return {"students": get_busy_students()}, 200
    except Exception as e:
        return {"error": str(e)}, 400


@report_bp.get("/lecturers/busy")
@jwt_required()
def busy_lecturers():
    user, err, code = _require_admin(get_jwt_identity())
    if err:
        return err, code
    try:
        return {"lecturers": get_busy_lecturers()}, 200
    except Exception as e:
        return {"error": str(e)}, 400


@report_bp.get("/courses/most-enrolled")
@jwt_required()
def most_enrolled_courses():
    user, err, code = _require_admin(get_jwt_identity())
    if err:
        return err, code
    try:
        return {"courses": get_most_enrolled_courses()}, 200
    except Exception as e:
        return {"error": str(e)}, 400


@report_bp.get("/students/top")
@jwt_required()
def top_students():
    user, err, code = _require_admin(get_jwt_identity())
    if err:
        return err, code
    try:
        return {"students": get_top_students()}, 200
    except Exception as e:
        return {"error": str(e)}, 400