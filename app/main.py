from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
import logging
from .routes import auth_bp, course_bp, event_bp, forum_bp, thread_bp, content_bp, assignment_bp, report_bp

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Get static folder path
static_folder = os.path.join(os.path.dirname(__file__), '../frontend/dist')
logger.info(f"Static folder path: {static_folder}")
logger.info(f"Static folder exists: {os.path.exists(static_folder)}")

if os.path.exists(static_folder):
    app.static_folder = static_folder
    app.static_url_path = ''
    logger.info("Static folder configured successfully")
else:
    logger.warning("Frontend dist folder not found - static files will not be served")

# CORS Configuration
CORS(app, origins=[
    "http://localhost:5173",
    "http://localhost:5000",
    "https://vleclone.vercel.app",
    "*"
])

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY", "dev-secret-key")
jwt = JWTManager(app)

# Register API blueprints FIRST (they have /auth, /courses prefixes)
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(course_bp, url_prefix='/api')
app.register_blueprint(event_bp, url_prefix='/api')
app.register_blueprint(forum_bp, url_prefix='/api')
app.register_blueprint(thread_bp, url_prefix='/api')
app.register_blueprint(content_bp, url_prefix='/api')
app.register_blueprint(assignment_bp, url_prefix='/api')
app.register_blueprint(report_bp, url_prefix='/api')

# Serve frontend static files (registered LAST as catch-all)
@app.route('/')
def index():
    try:
        return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        logger.error(f"Error serving index.html: {e}")
        return {'error': 'Frontend not found'}, 503

@app.route('/<path:path>')
def serve_static(path):
    # Block API routes from being served as static files
    if path.startswith('api/'):
        return {'error': 'Not found'}, 404
    
    try:
        file_path = os.path.join(app.static_folder, path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return send_from_directory(app.static_folder, path)
        # Return index.html for SPA routing
        return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        logger.error(f"Error serving {path}: {e}")
        try:
            return send_from_directory(app.static_folder, 'index.html')
        except:
            return {'error': 'Frontend not found'}, 503
