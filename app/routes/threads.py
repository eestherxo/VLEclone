from flask import Blueprint, request
from app.services.thread_service import get_all_threads, get_thread, create_thread, delete_thread

thread_bp = Blueprint("thread", __name__, url_prefix="/threads")

@thread_bp.get("/forum/<int:forum_id>")
def fetch_all_threads(forum_id):
    try:
        threads = get_all_threads(forum_id)
        return {"threads": threads}, 200
    except Exception as e:
        return {"error": str(e)}, 400

@thread_bp.get("/<int:thread_id>")
def fetch_thread(thread_id):
    try:
        thread = get_thread(thread_id)
        return {"thread": thread}, 200
    except Exception as e:
        return {"error": str(e)}, 400

@thread_bp.post("/")
def add_thread():
    try:
        forum_id = request.json.get("forumID", None)
        thread_title = request.json.get("threadTitle", None)
        content = request.json.get("content", None)
        if not forum_id or not thread_title or not content:
            return {"error": "Missing required fields"}, 400
        create_thread(forum_id, thread_title, content)
        return {"message": "Thread created successfully"}, 201
    except Exception as e:
        return {"error": str(e)}, 400

@thread_bp.delete("/<int:thread_id>")
def remove_thread(thread_id):
    try:
        delete_thread(thread_id)
        return {"message": "Thread deleted successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 400