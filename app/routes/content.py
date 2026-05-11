from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.services.user_service import get_user
from app.services.content_services import (
    create_section,
    add_section_item,
    get_course_content,
    get_section,
)

content_bp = Blueprint('content', __name__, url_prefix='/content')


# GET /content/course/<course_code>   ← frontend calls this
@content_bp.get('/course/<course_code>')
@jwt_required()
def list_content(course_code):
    user_id = get_jwt_identity()
    user = get_user(user_id)
    if not user:
        return {"error": "User not found"}, 404
    try:
        sections = get_course_content(course_code)
        return {"courseCode": course_code, "sections": sections}, 200
    except Exception as e:
        return {"error": str(e)}, 400


# POST /content/sections/<course_code>
@content_bp.post('/sections/<course_code>')
@jwt_required()
def create_new_section(course_code):
    user_id = get_jwt_identity()
    user = get_user(user_id)
    if not user:
        return {"error": "User not found"}, 404

    # Admins are also lecturers
    if user['role'].lower() not in ('lecturer', 'admin'):
        return {"error": "Only lecturers can create sections"}, 403

    section_name = request.json.get('sectionName')
    if not section_name:
        return {"error": "Missing sectionName"}, 400

    try:
        section_id = create_section(course_code, section_name)
        return {
            "message": "Section created successfully",
            "sectionID": section_id,
            "sectionName": section_name,
            "courseCode": course_code
        }, 201
    except Exception as e:
        return {"error": str(e)}, 400


# POST /content/sections/<section_id>/items
@content_bp.post('/sections/<int:section_id>/items')
@jwt_required()
def add_item_to_section(section_id):
    user_id = get_jwt_identity()
    user = get_user(user_id)
    if not user:
        return {"error": "User not found"}, 404

    if user['role'].lower() not in ('lecturer', 'admin'):
        return {"error": "Only lecturers can add content"}, 403

    item_name = request.json.get('itemName')
    item_type = request.json.get('itemType')
    content   = request.json.get('content')

    if not item_name or not item_type or not content:
        return {"error": "Missing required fields: itemName, itemType, content"}, 400

    try:
        section = get_section(section_id)
        if not section:
            return {"error": "Section not found"}, 404

        item_id = add_section_item(section_id, item_name, item_type, content)
        return {
            "message": "Content item added successfully",
            "itemID": item_id,
            "itemName": item_name,
            "itemType": item_type,
            "sectionID": section_id
        }, 201
    except Exception as e:
        return {"error": str(e)}, 400


# POST /content/create  ← frontend calls this for quick add
@content_bp.post('/create')
@jwt_required()
def create_content():
    user_id = get_jwt_identity()
    user = get_user(user_id)
    if not user:
        return {"error": "User not found"}, 404

    if user['role'].lower() not in ('lecturer', 'admin'):
        return {"error": "Only lecturers can add content"}, 403

    course_code  = request.json.get('courseCode')
    section_name = request.json.get('section') or 'General'
    item_name    = request.json.get('title')
    item_type    = request.json.get('type') or request.json.get('itemType')
    content      = request.json.get('url') or request.json.get('content')

    if not course_code or not item_name or not item_type or not content:
        return {"error": "Missing required fields"}, 400

    try:
        # Create section if needed, then add item
        section_id = create_section(course_code, section_name)
        item_id    = add_section_item(section_id, item_name, item_type, content)
        return {
            "message": "Content added successfully",
            "itemID": item_id,
            "title": item_name,
            "type": item_type,
            "section": section_name,
            "url": content
        }, 201
    except Exception as e:
        return {"error": str(e)}, 400
