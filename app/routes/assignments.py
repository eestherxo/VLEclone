from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.services.user_service import get_user
from app.services.assignment_service import (
    get_assignments_by_course, create_assignment,
    submit_assignment, grade_assignment, get_submissions
)

assignment_bp = Blueprint("assignments", __name__, url_prefix="/assignments")


@assignment_bp.get("/course/<course_code>")
@jwt_required()
def get_course_assignments(course_code):
    try:
        assignments = get_assignments_by_course(course_code)
        return {"assignments": assignments}, 200
    except Exception as e:
        return {"error": str(e)}, 400


@assignment_bp.post("/create")
@jwt_required()
def create_course_assignment():
    user_id = get_jwt_identity()
    user = get_user(user_id)

    if not user or user["role"].lower() not in ['lecturer', 'admin']:
        return {"error": "Only lecturers can create assignments"}, 403

    course_code      = request.json.get("courseCode")
    assignment_name  = request.json.get("assignmentName")
    due_date         = request.json.get("dueDate")

    if not course_code or not assignment_name or not due_date:
        return {"error": "Missing required fields"}, 400

    try:
        assignment_id = create_assignment(course_code, assignment_name, due_date)
        return {"message": "Assignment created successfully", "assignmentID": assignment_id}, 201
    except Exception as e:
        return {"error": str(e)}, 400


@assignment_bp.post("/<int:assignment_id>/submit")
@jwt_required()
def submit(assignment_id):
    user_id = get_jwt_identity()
    user = get_user(user_id)

    if not user or user["role"].lower() != 'student':
        return {"error": "Only students can submit assignments"}, 403

    content   = request.json.get("content")
    file_path = request.json.get("filePath", content)

    if not file_path:
        return {"error": "Missing submission content"}, 400

    try:
        submit_assignment(user_id, assignment_id, file_path)
        return {"message": "Assignment submitted successfully"}, 201
    except Exception as e:
        return {"error": str(e)}, 400


@assignment_bp.post("/<int:assignment_id>/grade/<int:student_id>")
@jwt_required()
def grade(assignment_id, student_id):
    user_id = get_jwt_identity()
    user = get_user(user_id)

    if not user or user["role"].lower() not in ['lecturer', 'admin']:
        return {"error": "Only lecturers can grade assignments"}, 403

    grade_value = request.json.get("grade")
    if grade_value is None:
        return {"error": "Missing grade value"}, 400

    try:
        grade_assignment(user_id, assignment_id, student_id, grade_value)
        return {"message": "Grade saved successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 400


@assignment_bp.get("/<int:assignment_id>/submissions")
@jwt_required()
def submissions(assignment_id):
    user_id = get_jwt_identity()
    user = get_user(user_id)

    if not user or user["role"].lower() not in ['lecturer', 'admin']:
        return {"error": "Only lecturers can view submissions"}, 403

    try:
        subs = get_submissions(assignment_id)
        return {"submissions": subs}, 200
    except Exception as e:
        return {"error": str(e)}, 400