from flask import Flask 
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from .config import Config
from .routes import auth_bp, course_bp, event_bp, content_bp, assignment_bp, forum_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  

    # Proper CORS config — allows Vue dev server
    CORS(app, resources={
        r"/*": {
            "origins": [
                "http://localhost:5173",
                "http://127.0.0.1:5173",
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })

    jwt = JWTManager(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(event_bp)
    app.register_blueprint(content_bp)
    app.register_blueprint(assignment_bp)
    app.register_blueprint(forum_bp)   # ← add this

    @app.get("/")
    def hello():
        return {"message": "Hello, World!"}, 200

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)