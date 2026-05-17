from flask import Flask 
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .db import config
from .routes import auth_bp, course_bp, event_bp, forum_bp, thread_bp, content_bp, assignment_bp



app = Flask(__name__)

# CORS Configuration
CORS(app, origins=["http://localhost:5173"])

# JWT Configuration
app.config['JWT_SECRET_KEY'] = config["JWT_SECRET_KEY"]
jwt = JWTManager(app)

# Endpoints
app.register_blueprint(auth_bp)
app.register_blueprint(course_bp)
app.register_blueprint(event_bp)
app.register_blueprint(forum_bp)
app.register_blueprint(thread_bp)
app.register_blueprint(content_bp)
app.register_blueprint(assignment_bp)