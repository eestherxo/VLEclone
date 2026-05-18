from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from .routes import auth_bp, course_bp, event_bp, forum_bp, thread_bp, content_bp, assignment_bp, report_bp


app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), '../frontend/dist'), static_url_path='')

# CORS Configuration
CORS(app, origins=[
    "http://localhost:5173",
    "http://localhost:5000",
    "https://vleclone.vercel.app"
])

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)

# Endpoints
app.register_blueprint(auth_bp)
app.register_blueprint(course_bp)
app.register_blueprint(event_bp)
app.register_blueprint(forum_bp)
app.register_blueprint(thread_bp)
app.register_blueprint(content_bp)
app.register_blueprint(assignment_bp)
app.register_blueprint(report_bp)

# Serve frontend static files
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')
