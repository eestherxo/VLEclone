from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.services.forum_service import get_all_forums, get_forum, create_forum, delete_forum
from app.services.user_service import get_user

forum_bp = Blueprint("forum", __name__, url_prefix="/forums")

@forum_bp.get("/course/<course_code>")
@jwt_required()
def fetch_all_forums(course_code):
    try:
        forums = get_all_forums(course_code)
        return {"forums": forums}, 200
    except Exception as e:
        return {"error": str(e)}, 400

@forum_bp.get("/<int:forum_id>")
@jwt_required()
def fetch_forum(forum_id):
    try:
        forum = get_forum(forum_id)
        return {"forum": forum}, 200
    except Exception as e:
        return {"error": str(e)}, 400

@forum_bp.post("/course")
@jwt_required() 
def add_forum():
    user_id = get_jwt_identity()  
    user = get_user(user_id)
    print(f"DEBUG: user_id={user_id}, user={user}")  # 👈 add this
    if not user or user["role"].lower() not in ['lecturer', 'admin']:
        return {"error": "Only lecturers or admins can create forums"}, 403
    
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
@jwt_required()
def remove_forum(forum_id):
    try:
        delete_forum(forum_id)
        return {"message": "Forum deleted successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 400