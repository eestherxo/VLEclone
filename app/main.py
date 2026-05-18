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

# Get static folder path - use absolute path for better reliability
base_dir = os.path.dirname(os.path.abspath(__file__))
static_folder = os.path.join(base_dir, '../frontend/dist')
static_folder = os.path.abspath(static_folder)

logger.info(f"Static folder path: {static_folder}")
logger.info(f"Static folder exists: {os.path.exists(static_folder)}")

# Always set static folder (even if it doesn't exist yet)
app.static_folder = static_folder
app.static_url_path = ''

if os.path.exists(static_folder):
    logger.info("Static folder configured successfully")
    # Check if index.html exists
    index_path = os.path.join(static_folder, 'index.html')
    logger.info(f"index.html exists: {os.path.exists(index_path)}")
else:
    logger.warning(f"Frontend dist folder not found at {static_folder}")
    logger.warning("Frontend will be unavailable until built")

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
        index_path = os.path.join(app.static_folder, 'index.html')
        if not os.path.exists(index_path):
            logger.error(f"index.html not found at {index_path}")
            return {
                'status': 'API Server Running',
                'message': 'Frontend not built yet. Build the frontend with: cd frontend && npm run build',
                'api_endpoints': '/api/auth, /api/courses, /api/forums, etc.'
            }, 200
        return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        logger.error(f"Error serving index.html: {e}")
        return {
            'status': 'API Server Running',
            'error': str(e),
            'api_endpoints': '/api/auth, /api/courses, /api/forums, etc.'
        }, 200

@app.route('/<path:path>')
def serve_static(path):
    # Block API routes from being served as static files
    if path.startswith('api/'):
        return {'error': 'Not found'}, 404
    
    # Don't try to serve if static folder doesn't exist
    if not os.path.exists(app.static_folder):
        try:
            return {
                'status': 'API Server Running',
                'message': 'Frontend not built yet',
                'path': path,
                'api_available': True
            }, 200
        except:
            return {'error': 'Not found'}, 404
    
    try:
        file_path = os.path.join(app.static_folder, path)
        # Security check - ensure we're not escaping the static folder
        if not os.path.abspath(file_path).startswith(os.path.abspath(app.static_folder)):
            return {'error': 'Not found'}, 404
            
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return send_from_directory(app.static_folder, path)
        
        # Return index.html for SPA routing
        index_path = os.path.join(app.static_folder, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(app.static_folder, 'index.html')
        
        return {'error': 'Not found'}, 404
    except Exception as e:
        logger.error(f"Error serving {path}: {e}")
        return {'error': 'Not found'}, 404
