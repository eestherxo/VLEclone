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


