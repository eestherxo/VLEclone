from flask import Flask 
from flask_jwt_extended import JWTManager
from .config import Config
from .routes import auth_bp, course_bp, event_bp, content_bp, assignment_bp


app = Flask(__name__)
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


if __name__== "__main__":
    app.run(debug=True)