from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.services.user_service import get_user
from app.services.course_service import *

course_bp = Blueprint('course', __name__, url_prefix='/courses')


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
        return {"message": "Course created successfully"}, 201
    except Exception as e:
        return {"error": str(e)}, 400

    
@course_bp.get("/list")
@jwt_required()
def list_courses():
    user_id = get_jwt_identity()
    user = get_user(user_id)
    
    if not user:
        return {"error": "User not found"}, 404
    
    courses = get_courses()
    
    return {"courses": courses}, 200


@course_bp.get("/list/<int:student_id>")
@jwt_required()
def list_student_courses(student_id):
    user_id = get_jwt_identity()
    user = get_user(user_id)
    
    if not user:
        return {"error": "User not found"}, 404
    
    courses = get_student_courses(student_id)
    
    return {"courses": courses}, 200
    

@course_bp.get("/list/<int:lecturer_id>")
@jwt_required()
def list_lecturer_courses(lecturer_id):
    user_id = get_jwt_identity()
    user = get_user(user_id)
    
    if not user:
        return {"error": "User not found"}, 404
    
    courses = get_lecturer_courses(lecturer_id)
    
    return {"courses": courses}, 200


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


@course_bp.post("/enroll-student")
@jwt_required()
def enroll_student():
    user_id = get_jwt_identity()
    user = get_user(user_id)
    
    if not user or user['role'].lower() == 'lecturer':
        return {"error": "Lecturers can not enroll students"}, 403
    
    student_id = request.json.get('studentId')
    course_code = request.json.get('courseCode')
    
    if not student_id or not course_code:
        return {"error": "Missing required fields"}, 400
    
    try:
        insert_enroll(student_id, course_code)
        return {"message": "Student enrolled successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 400


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