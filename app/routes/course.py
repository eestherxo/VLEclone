from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.services.user_service import get_user
from app.services.course_service import *

course_bp = Blueprint('course', __name__, url_prefix='/courses')


# GET /courses/my  — returns courses relevant to the logged-in user by role
@course_bp.get("/my")
@jwt_required()
def get_my_courses():
    user_id = get_jwt_identity()
    user = get_user(user_id)

    if not user:
        return {"error": "User not found"}, 404

    role = user['role'].lower()

    if role == 'student':
        courses = get_student_courses(user_id)
    elif role == 'lecturer':
        courses = get_lecturer_courses(user_id)
    elif role == 'admin':
        courses = get_courses()   # admins see all courses
    else:
        return {"error": "Invalid user role"}, 400

    return {"courses": courses}, 200


# GET /courses/list
@course_bp.get("/list")
@jwt_required()
def list_courses():
    courses = get_courses()
    return {"courses": courses}, 200


# GET /courses/list/student/<id>
@course_bp.get("/list/student/<int:student_id>")
@jwt_required()
def list_student_courses(student_id):
    courses = get_student_courses(student_id)
    return {"courses": courses}, 200


# GET /courses/list/lecturer/<id>
@course_bp.get("/list/lecturer/<int:lecturer_id>")
@jwt_required()
def list_lecturer_courses(lecturer_id):
    courses = get_lecturer_courses(lecturer_id)
    return {"courses": courses}, 200


# POST /courses/create  (admin only)
@course_bp.post("/create")
@jwt_required()
def create_course():
    user_id = get_jwt_identity()
    user = get_user(user_id)

    if not user or user['role'].lower() != 'admin':
        return {"error": "Only admins can create courses"}, 403

    course_code = request.json.get('courseCode')
    course_name = request.json.get('courseName')

    if not course_code or not course_name:
        return {"error": "Missing required fields"}, 400

    try:
        insert_course(course_code, course_name)
        return {"message": "Course created successfully", "courseCode": course_code, "courseName": course_name}, 201
    except Exception as e:
        return {"error": str(e)}, 400


# POST /courses/assign-lecturer  (admin only)
@course_bp.post("/assign-lecturer")
@jwt_required()
def assign_lecturer():
    user_id = get_jwt_identity()
    user = get_user(user_id)

    if not user or user['role'].lower() != 'admin':
        return {"error": "Only admins can assign lecturers"}, 403

    lecturer_id = request.json.get('lecturerId')
    course_code = request.json.get('courseCode')

    if not lecturer_id or not course_code:
        return {"error": "Missing required fields"}, 400

    try:
        insert_teaches(lecturer_id, course_code)
        return {"message": "Lecturer assigned successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 400


# POST /courses/enroll-student
@course_bp.post("/enroll-student")
@jwt_required()
def enroll_student():
    user_id = get_jwt_identity()
    user = get_user(user_id)

    if not user or user['role'].lower() == 'lecturer':
        return {"error": "Lecturers cannot enroll students"}, 403

    student_id  = request.json.get('studentId')
    course_code = request.json.get('courseCode')

    if not student_id or not course_code:
        return {"error": "Missing required fields"}, 400

    try:
        insert_enroll(student_id, course_code)
        return {"message": "Student enrolled successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 400


# GET /courses/members/<course_code>
@course_bp.get("/members/<course_code>")
@jwt_required()
def list_members(course_code):
    user_id = get_jwt_identity()
    user = get_user(user_id)

    if not user:
        return {"error": "User not found"}, 404

    try:
        members = get_course_members(course_code)
        return {"members": members}, 200
    except Exception as e:
        return {"error": str(e)}, 400
