from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.events_service import *
from app.services.user_service import get_user


event_bp = Blueprint("events", __name__, url_prefix="/events")


@event_bp.get("/course/<course_code>")
@jwt_required()
def course_events(course_code):
    try:
        events = get_course_events(course_code)
        return {"events": events}, 200
    except Exception as e:
        return {"error": str(e)}, 400


@event_bp.get("/student/<student_id>/date/<due_date>")
@jwt_required()
def student_events_by_date(student_id, due_date):
    try:
        events = get_student_events_by_date(student_id, due_date)
        return {"events": events}, 200
    except Exception as e:
        return {"error": str(e)}, 400


@event_bp.post("/course")
@jwt_required()
def create_course_event():
    user_id = get_jwt_identity()
    user = get_user(user_id)

    if not user or user["role"].lower() != 'lecturer':
        return {"error": "Only lecturers can create course events"}, 403
    
    course_code = request.json.get("courseCode", None)
    event_name = request.json.get("eventName", None)
    created_date = request.json.get("createdDate", None)
    due_date = request.json.get("dueDate", None)

    if not course_code or not event_name or not created_date or not due_date:
        return {"error": "Missing required fields"}, 400
    
    try:
        insert_course_event(course_code, event_name, created_date, due_date)
        return {"message": "Course event created successfully"}, 201
    except Exception as e:
        return {"error": str(e)}, 400


# @event_bp.post("/assignment/submit")
# @jwt_required()
# def submit_assignment_endpoint():
#     user_id = get_jwt_identity()
#     user = get_user(user_id)

#     if not user or user["role"].lower() != 'student':
#         return {"error": "Only students can submit assignments"}, 403

#     student_id = request.json.get("studentID", None)
#     assignment_id = request.json.get("assignmentID", None)
#     file_path = request.json.get("filePath", None)

#     if not student_id or not assignment_id or not file_path:
#         return {"error": "Missing required fields"}, 400

#     try:
#         submit_assignment(student_id, assignment_id, file_path)
#         return {"message": "Assignment submitted successfully"}, 201
#     except Exception as e:
#         return {"error": str(e)}, 400  # 👈 this was missing

# @event_bp.post("/assignment/grade")
# @jwt_required()
# def grade_assignment_endpoint():
#     user_id = get_jwt_identity()
#     user = get_user(user_id)

#     if not user or user["role"].lower() != 'lecturer':
#         return {"error": "Only lecturers can grade assignments"}, 403

#     assignment_id = request.json.get("assignmentID", None)
#     student_id = request.json.get("studentID", None)
#     grade_value = request.json.get("grade", None)

#     if not assignment_id or not student_id or grade_value is None:
#         return {"error": "Missing required fields"}, 400

#     if not lecturer_owns_event(user_id, assignment_id):
#         return {"error": "You do not have permission to grade this assignment"}, 403

#     try:
#         grade_assignment(user_id, assignment_id, student_id, grade_value)
#         return {"message": "Assignment graded successfully"}, 201
#     except Exception as e:
#         return {"error": str(e)}, 400
    
# @event_bp.post("/assignment")
# @jwt_required()
# def create_assignment():
#     user_id = get_jwt_identity()
#     user = get_user(user_id)

#     if not user or user["role"].lower() != 'lecturer':
#         return {"error": "Only lecturers can create assignments"}, 403

#     event_id = request.json.get("eventID", None)

#     if not event_id:
#         return {"error": "Missing required fields"}, 400

#     try:
#         create_assignment(event_id)
#         return {"message": "Assignment created successfully"}, 201
#     except Exception as e:
#         return {"error": str(e)}, 400
