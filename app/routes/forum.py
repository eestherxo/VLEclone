from flask import Blueprint, request
from app.services.forum_service import get_all_forums, get_forum, create_forum, delete_forum

forum_bp = Blueprint("forum", __name__, url_prefix="/forums")

@forum_bp.get("/")
def fetch_all_forums():
    try:
        forums = get_all_forums()
        return {"forums": forums}, 200
    except Exception as e:
        return {"error": str(e)}, 400

@forum_bp.get("/<int:forum_id>")
def fetch_forum(forum_id):
    try:
        forum = get_forum(forum_id)
        return {"forum": forum}, 200
    except Exception as e:
        return {"error": str(e)}, 400

@forum_bp.post("/")
def add_forum():
    try:
        course_code = request.json.get("courseCode", None)
        forum_name = request.json.get("forumName", None)
        if not course_code or not forum_name:
            return {"error": "Missing required fields"}, 400
        create_forum(course_code, forum_name)
        return {"message": "Forum created successfully"}, 201
    except Exception as e:
        return {"error": str(e)}, 400

@forum_bp.delete("/<int:forum_id>")
def remove_forum(forum_id):
    try:
        delete_forum(forum_id)
        return {"message": "Forum deleted successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 400