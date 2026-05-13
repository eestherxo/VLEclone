from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.user_service import get_user, insert_user


registration_bp = Blueprint("register", __name__, url_prefix="/register")

@registration_bp.post("/student")
@jwt_required()
def enroll_student():
    pass