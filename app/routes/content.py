from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.user_service import get_user
from app.services.content_service import *

content_bp = Blueprint("content", __name__, url_prefix="/course/<course_code>/content")

ALLOWED_TYPES = {"link", "file", "slide"}

# Create a new section
@content_bp.post("/section/create")
@jwt_required()
def create_section():
    user_id = get_jwt_identity()
    user = get_user(user_id)

    if not user or user["role"].lower() != "lecturer":
        return {"error": "Only lecturers can add course content"}, 403

    course_code = request.json.get("courseCode", None)
    sec_name = request.json.get("secName", None)

    if not course_code or not sec_name:
        return {"error": "Missing required fields"}, 400

    if not lecturer_teaches_course(user_id, course_code):
        return {"error": "You can only add content to courses you teach"}, 403

    try:
        sec_id = insert_section(course_code, sec_name)
        return {"message": "Section created successfully", "secID": sec_id}, 201
    except Exception as e:
        return {"error": str(e)}, 400


# Add a content item (link / file / slide) to a section
@content_bp.post("/section/item/create")
@jwt_required()
def create_course_content():
    user_id = get_jwt_identity()
    user = get_user(user_id)

    if not user or user["role"].lower() != "lecturer":
        return {"error": "Only lecturers can add course content"}, 403

    sec_id = request.json.get("secID", None)
    content_name = request.json.get("contentName", None)
    content_type = request.json.get("type", None)
    content = request.json.get("content", None)

    if not sec_id or not content_name or not content_type or not content:
        return {"error": "Missing required fields"}, 400

    if content_type.lower() not in ALLOWED_TYPES:
        return {
            "error": f"Invalid type. Must be one of: {', '.join(ALLOWED_TYPES)}"
        }, 400

    # Ensure the section exists and the lecturer teaches its course
    course_code = get_course_code_for_section(sec_id)
    if not course_code:
        return {"error": "Section not found"}, 404
    if not lecturer_teaches_course(user_id, course_code):
        return {"error": "You can only add content to courses you teach"}, 403

    try:
        content_id = insert_course_content(
            sec_id, content_name, content_type.lower(), content
        )
        return {
            "message": "Course content added successfully",
            "contentID": content_id,
        }, 201
    except Exception as e:
        return {"error": str(e)}, 400


# Show all course content (separated by section)
@content_bp.get("/show")
@jwt_required()
def get_course_content(course_code):
    user_id = get_jwt_identity()
    user = get_user(user_id)

    if not user:
        return {"error": "Unauthorized"}, 401

    try:
        sections = get_course_content_by_course(course_code)
        return {"courseCode": course_code, "sections": sections}, 200
    except Exception as e:
        return {"error": str(e)}, 400