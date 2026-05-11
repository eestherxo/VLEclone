from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.services.user_service import get_user
from app.services.forum_service import (
    get_course_forum,
    insert_forum,
    get_forum_threads,
    insert_thread,
    insert_reply
)

forum_bp = Blueprint('forum', __name__, url_prefix="/forums")


# GET /forums/course/<course_code>
@forum_bp.get("/course/<course_code>")
@jwt_required()
def list_course_forums(course_code):
    user_id = get_jwt_identity()
    user = get_user(user_id)
    if not user:
        return {"error": "User not found"}, 404
    try:
        forums = get_course_forum(course_code)
        return {"forums": forums}, 200
    except Exception as e:
        return {"error": str(e)}, 400


# POST /forums/create
@forum_bp.post("/create")
@jwt_required()
def create_forum():
    user_id = get_jwt_identity()
    user = get_user(user_id)
    if not user:
        return {"error": "User not found"}, 404

    course_code = request.json.get("courseCode")
    forum_name  = request.json.get("forumName") or request.json.get("title")
    if not course_code or not forum_name:
        return {"error": "Missing required fields: courseCode, forumName"}, 400

    try:
        insert_forum(course_code, forum_name)
        return {"message": "Forum created successfully"}, 201
    except Exception as e:
        return {"error": str(e)}, 400


# GET /forums/<forum_id>/threads
@forum_bp.get("/<int:forum_id>/threads")
@jwt_required()
def list_forum_threads(forum_id):
    user_id = get_jwt_identity()
    user = get_user(user_id)
    if not user:
        return {"error": "User not found"}, 404
    try:
        threads = get_forum_threads(forum_id)
        return {"threads": threads}, 200
    except Exception as e:
        return {"error": str(e)}, 400


# POST /forums/<forum_id>/threads
@forum_bp.post("/<int:forum_id>/threads")
@jwt_required()
def create_thread(forum_id):
    user_id = get_jwt_identity()
    user = get_user(user_id)
    if not user:
        return {"error": "User not found"}, 404

    thread_title   = request.json.get("title") or request.json.get("threadTitle")
    thread_content = request.json.get("content") or request.json.get("threadContent")
    if not thread_title or not thread_content:
        return {"error": "Missing required fields: title, content"}, 400

    try:
        insert_thread(forum_id, thread_title, thread_content, user_id)
        return {"message": "Thread created successfully"}, 201
    except Exception as e:
        return {"error": str(e)}, 400


# POST /forums/threads/<thread_id>/reply
@forum_bp.post("/threads/<int:thread_id>/reply")
@jwt_required()
def reply_to_thread(thread_id):
    user_id = get_jwt_identity()
    user = get_user(user_id)
    if not user:
        return {"error": "User not found"}, 404

    content = request.json.get("content")
    if not content:
        return {"error": "Missing required field: content"}, 400

    try:
        insert_reply(thread_id, user_id, content)
        return {"message": "Reply posted successfully"}, 201
    except Exception as e:
        return {"error": str(e)}, 400
