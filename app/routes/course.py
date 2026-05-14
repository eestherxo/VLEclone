from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.user_service import get_user
from app.services.course_service import *



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


@course_bp.post("/assign-lecturer")
@jwt_required()
def lecturer_assignment():
    user_id = get_jwt_identity()
    user = get_user(user_id)

    if not user or user["role"].lower() != 'admin':
        return {"error": "Only admins can assign lecturers"}, 403

    lecturer_id = request.json.get("lecturerId", None)
    course_code = request.json.get("courseCode", None)

    if not lecturer_id or not course_code:
        return {"error": "Missing required fields"}, 400
    
    existing_lecturer = check_course_lecturer(course_code)
    if existing_lecturer:
        return {"error": "Course already has a lecturer assigned"}, 400

    if existing_lecturer:
        return {"error": "Course already has a lecturer assigned"}, 400

    try:
        assign_lecturer(lecturer_id, course_code)
        return {"message": "Lecturer assigned successfully"}, 201
    except Exception as e:
        return {"error": str(e)}, 400


@course_bp.post("/enroll-student")
@jwt_required()
def enroll_student():
    user_id = get_jwt_identity()
    user = get_user(user_id)

    if not user or user["role"].lower() != 'student':
        return {"error": "Only students can enroll in courses"}, 403

    student_id = request.json.get("studentID", None)
    course_code = request.json.get("courseCode", None)

    if not student_id or not course_code:
        return {"error": "Missing required fields"}, 400

    try:
        enroll_student(student_id, course_code)
        return {"message": "Student enrolled successfully"}, 201
    except Exception as e:
        return {"error": str(e)}, 400


@course_bp.get("/members/<course_code>")
@jwt_required()
def course_members(course_code):
    try:
        members = get_course_members(course_code)
        return {"members": members}, 200
    except Exception as e:
        return {"error": str(e)}, 400