
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.user_service import get_user
from app.services.forum_service import *

forum_bp = Blueprint('forum', __name__, url_prefix="/forum")

@forum_bp.get("/<course_code>")
@jwt_required()
def list_course_forum(course_code):
    user_id = get_jwt_identity()
    user = get_user(user_id)

    if not user:
        return {"error": "User not found"}, 404
    try:
        forum = get_course_forum(course_code)
        return {"forum": forum}, 200
    except Exception as e:
        return {"error": str(e)}, 400
    
@forum_bp.post("/<create")
@jwt_required()
def create_forum(course_code, forum_name):
    user_id = get_jwt_identity()
    user = get_user(user_id)

    if not user and user['role'] != 'lecturer' and user['role'] != 'student':
        return {"error": "Only lecturers and students can create forums"}, 403

    course_code = request.json.get("courseCode")
    forum_name = request.json.get("forumName")
    if not course_code or not forum_name:
        return {"error": "Missing required fields"}, 400
    
    try:
        insert_forum(course_code, forum_name)
        return {"message": "Forum created successfully"}, 201
    except Exception as e:
        return {"error": str(e)}, 400


@forum_bp.post("/threads/<int:forum_id>")
@jwt_required()
def list_forum_threads(forum_id,):
    user_id = get_jwt_identity()
    user = get_user(user_id)

    if not user:
        return {"error": "User not found"}, 404
    try:
        threads = get_forum_threads(forum_id)
        return {"threads": threads}, 200
    except Exception as e:
        return {"error": str(e)}, 400
    
@forum_bp.post("/threads/create")
@jwt_required()
def create_thread(forum_id, thread_title, thread_content):
    user_id = get_jwt_identity()
    user = get_user(user_id)

    if not user and user['role'] != 'lecturer' and user['role'] != 'student':
        return {"error": "Only lecturers and students can create threads"}, 403

    forum_id = request.json.get("forumId")
    thread_title = request.json.get("threadTitle")
    thread_content = request.json.get("threadContent")
    if not forum_id or not thread_title or not thread_content:
        return {"error": "Missing required fields"}, 400
    
    try:
        insert_thread(forum_id, thread_title, thread_content)
        return {"message": "Thread created successfully"}, 201
    except Exception as e:
        return {"error": str(e)}, 400