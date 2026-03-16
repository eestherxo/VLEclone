from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.user_service import get_user
from app.services.event_service import get_course_events, get_student_events, insert_event

event_bp = Blueprint('event', __name__, url_prefix="/events")

@event_bp.get("/<course_code>")
@jwt_required()
def list_course_events(course_code):
    user_id = get_jwt_identity()
    user = get_user(user_id)

    if not user:
        return {"error": "User not found"}, 404

    try:
        events = get_course_events(course_code)
        return {"events": events}, 200
    except Exception as e:
        return {"error", str(e)}, 400
    

@event_bp.get("/<event_date>/student/<student_id>")
@jwt_required()
def list_student_events(student_id, event_date):
    user_id = get_jwt_identity()
    user = get_user(user_id)

    if not user:
        return {"error": "User not found"}, 404

    try:
        events = get_student_events(student_id, event_date)
        return {"events": events}, 200
    except Exception as e:
        return {"error", str(e)}, 400


@event_bp.post("/create")
@jwt_required()
def create_event(course_code, event_name, event_date):
    user_id = get_jwt_identity()
    user = get_user(user_id)

    if not user and user['role'] != 'lecturer':
        return {"error": "Only lecturers can create calendar events"}, 403

    course_code = request.json.get("courseCode")
    event_name = request.json.get("eventName")
    event_date = request.json.get("eventDate")

    if not course_code or not event_name or not event_date:
        return {"error": "Missing required fields"}, 400
    
    try:
        insert_event(course_code, event_name, event_date)
        return {"message": "Event created successfully"}, 201
    except Exception as e:
        return {"error": str(e)}, 400
        


    