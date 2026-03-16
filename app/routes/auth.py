from flask_jwt_extended import create_access_token
from flask import Blueprint, request
from app.services.user_service import verify_user, insert_user


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")



@auth_bp.post("/register")
def register():
    user_id = request.json.get("userID", None)
    full_name = request.json.get("Name", None)
    password = request.json.get("password", None)
    role = request.json.get("role", None)

    if not user_id or not full_name or not password or not role:
        return {"error": "Missing required fields"}, 400
    
    parts = full_name.strip().split(maxsplit=1)
    if len(parts) < 2:
        return {"error": "Provide both first and last name"}, 400
    first_name, last_name = parts[0], parts[1]
    
    try:
        insert_user(user_id, first_name, last_name, password, role)
        token = create_access_token(identity=user_id)
        return {"message": "User registered successfully", "access_token": token}, 201
    except Exception as e:
        return {"error": str(e)}, 400
    


@auth_bp.post("/login")
def login():
    user_id = request.json.get("userID", None)
    password = request.json.get("password", None)

    if not user_id or not password:
        return {"error": "Missing userID or password"}, 400

    # Verifiy credentials
    user = verify_user(user_id, password)
    if not user:
        return {"error": "Invalid Credentials"}, 401
    
    # Create JWT token 
    token = create_access_token(identity=user_id)

    return {"access_token": token, }, 200


