from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.user_service import get_user
from app.services.course_service import get_courses, insert_course, get_student_courses, get_lecturer_courses


course_bp = Blueprint("courses", __name__, url_prefix="/courses")


@course_bp.post("/create")
@jwt_required() 
def create_course():
    user_id = get_jwt_identity()
    user = get_user(user_id)

    if not user or user["role"].lower() != 'admin':
        return {"error": "Only admins can create courses"}, 403

    course_code = request.json.get("courseCode", None)
    course_name = request.json.get("courseName", None)

    if not course_code or not course_name:
        return {"error": "Missing required fields"}, 400

    try:
        insert_course(course_code, course_name)
        return {"message": "Course created successfully"}, 201
    except Exception as e:
        return {"error": str(e)}, 400


@course_bp.get("/all")
@jwt_required()
def all_courses():
    try:
        course = get_courses()
        return {"courses": course}, 200
    except Exception as e:
        return {"error": str(e)}, 400


@course_bp.get("/student/<student_id>")
@jwt_required()
def student_courses(student_id):
    try:
        courses = get_student_courses(student_id)
        return {"courses": courses}, 200
    except Exception as e:
        return {"error": str(e)}, 400


@course_bp.get("/lecturer/<lecturer_id>")
@jwt_required()
def lecturer_courses(lecturer_id):
    try:
        courses = get_lecturer_courses(lecturer_id)
        return {"courses": courses}, 200
    except Exception as e:
        return {"error": str(e)}, 400
