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


@content_bp.post('/sections/<course_code>')
@jwt_required()
def create_new_section(course_code):
    user_id = get_jwt_identity()
    user = get_user(user_id)
    
    if not user:
        return {"error": "User not found"}, 404
    
    if user['role'].lower() != 'lecturer':
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


@content_bp.post('/sections/<int:section_id>/items')
@jwt_required()
def add_item_to_section(section_id):
    user_id = get_jwt_identity()
    user = get_user(user_id)
    
    if not user:
        return {"error": "User not found"}, 404
    
    if user['role'].lower() != 'lecturer':
        return {"error": "Only lecturers can add content"}, 403
    
    item_name = request.json.get('itemName')
    item_type = request.json.get('itemType')  
    content = request.json.get('content')
    
    if not item_name or not item_type or not content:
        return {"error": "Missing required fields: itemName, itemType, content"}, 400
    
    
    try:
        # Verify section exists
        section = get_section(section_id)
        if not section:
            return {"error": "Section not found"}, 404
        
        # Add the item
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


@content_bp.get('/<course_code>')
@jwt_required()
def list_content(course_code):
    user_id = get_jwt_identity()
    user = get_user(user_id)
    
    if not user:
        return {"error": "User not found"}, 404
    
    try:
        sections = get_course_content(course_code)
        return {
            "courseCode": course_code,
            "sections": sections
        }, 200
    except Exception as e:
        return {"error": str(e)}, 400



