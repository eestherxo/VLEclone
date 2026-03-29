from flask import Flask 
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from .config import Config
from .routes import auth_bp, course_bp, event_bp, content_bp, assignment_bp

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)
    jwt = JWTManager(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(event_bp)
    app.register_blueprint(content_bp)
    app.register_blueprint(assignment_bp)
    

    @app.get("/")
    def hello():
        return {"message": "Hello, World!"}, 200

    return app

if __name__== "__main__":
    app = create_app()
    app.run(debug=True)