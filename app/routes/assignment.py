from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.services.user_service import get_user
from app.services.assignment_service import (
    create_assignment,
    get_course_assignments,
    submit_assignment,
    grade_assignment,
    get_student_grades,
    get_student_final_average,
    get_assignment_submissions,
    check_student_submission
)

assignment_bp = Blueprint('assignments', __name__, url_prefix='/assignments')


# POST /assignments/create
@assignment_bp.post('/create')
@jwt_required()
def create_new_assignment():
    user_id = get_jwt_identity()
    user = get_user(user_id)
    if not user:
        return {"error": "User not found"}, 404

    # Admins are also lecturers
    if user['role'].lower() not in ('lecturer', 'admin'):
        return {"error": "Only lecturers can create assignments"}, 403

    course_code     = request.json.get('courseCode')
    assignment_name = request.json.get('assignmentName') or request.json.get('title')
    due_date        = request.json.get('dueDate') or request.json.get('due_date')

    if not course_code or not assignment_name or not due_date:
        return {"error": "Missing required fields: courseCode, assignmentName, dueDate"}, 400

    try:
        assignment_id = create_assignment(course_code, assignment_name, due_date, user_id)
        return {
            "message": "Assignment created successfully",
            "id": assignment_id,
            "assignmentID": assignment_id,
            "title": assignment_name,
            "assignmentName": assignment_name,
            "courseCode": course_code,
            "due_date": due_date,
            "dueDate": due_date
        }, 201
    except Exception as e:
        return {"error": str(e)}, 400


# GET /assignments/course/<course_code>
@assignment_bp.get('/course/<course_code>')
@jwt_required()
def list_course_assignments(course_code):
    user_id = get_jwt_identity()
    user = get_user(user_id)
    if not user:
        return {"error": "User not found"}, 404
    try:
        assignments = get_course_assignments(course_code)
        return {"courseCode": course_code, "assignments": assignments}, 200
    except Exception as e:
        return {"error": str(e)}, 400


# POST /assignments/<id>/submit
@assignment_bp.post('/<int:assignment_id>/submit')
@jwt_required()
def submit_assignment_endpoint(assignment_id):
    user_id = get_jwt_identity()
    user = get_user(user_id)
    if not user:
        return {"error": "User not found"}, 404

    if user['role'].lower() != 'student':
        return {"error": "Only students can submit assignments"}, 403

    try:
        result = submit_assignment(user_id, assignment_id)
        if isinstance(result, dict) and "error" in result:
            return result, 400
        return {"message": "Assignment submitted successfully", "assignmentID": assignment_id, "studentID": user_id}, 201
    except Exception as e:
        return {"error": str(e)}, 400


# POST /assignments/<id>/grade/<student_id>  ← matches frontend call
@assignment_bp.post('/<int:assignment_id>/grade/<int:student_id>')
@jwt_required()
def grade_student_assignment(assignment_id, student_id):
    user_id = get_jwt_identity()
    user = get_user(user_id)
    if not user:
        return {"error": "User not found"}, 404

    if user['role'].lower() not in ('lecturer', 'admin'):
        return {"error": "Only lecturers can grade assignments"}, 403

    grade = request.json.get('grade')
    if grade is None:
        return {"error": "Missing required field: grade"}, 400

    if not isinstance(grade, (int, float)) or grade < 0 or grade > 100:
        return {"error": "Grade must be a number between 0 and 100"}, 400

    try:
        grade_assignment(assignment_id, student_id, grade, user_id)
        return {"message": "Grade submitted successfully", "assignmentID": assignment_id, "studentID": student_id, "grade": grade}, 200
    except Exception as e:
        return {"error": str(e)}, 400


# GET /assignments/<id>/submissions
@assignment_bp.get('/<int:assignment_id>/submissions')
@jwt_required()
def list_assignment_submissions(assignment_id):
    user_id = get_jwt_identity()
    user = get_user(user_id)
    if not user:
        return {"error": "User not found"}, 404

    if user['role'].lower() not in ('lecturer', 'admin'):
        return {"error": "Only lecturers can view submissions"}, 403

    try:
        submissions = get_assignment_submissions(assignment_id)
        return {"assignmentID": assignment_id, "submissions": submissions}, 200
    except Exception as e:
        return {"error": str(e)}, 400


# GET /assignments/student/<student_id>/grades
@assignment_bp.get('/student/<int:student_id>/grades')
@jwt_required()
def get_student_assignment_grades(student_id):
    user_id = get_jwt_identity()
    user = get_user(user_id)
    if not user:
        return {"error": "User not found"}, 404

    if user['role'].lower() == 'student' and int(user_id) != student_id:
        return {"error": "Students can only view their own grades"}, 403

    try:
        grades = get_student_grades(student_id)
        return {"studentID": student_id, "grades": grades}, 200
    except Exception as e:
        return {"error": str(e)}, 400


# GET /assignments/student/<student_id>/average
@assignment_bp.get('/student/<int:student_id>/average')
@jwt_required()
def get_student_average(student_id):
    user_id = get_jwt_identity()
    user = get_user(user_id)
    if not user:
        return {"error": "User not found"}, 404

    if user['role'].lower() == 'student' and int(user_id) != student_id:
        return {"error": "Students can only view their own average"}, 403

    course_code = request.args.get('courseCode')
    try:
        averages = get_student_final_average(student_id, course_code)
        return {"studentID": student_id, "courseCode": course_code, "gradeData": averages}, 200
    except Exception as e:
        return {"error": str(e)}, 400
