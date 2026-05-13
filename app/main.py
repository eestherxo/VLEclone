from flask import Flask 
from flask_jwt_extended import JWTManager
from .db import config
from .routes import auth_bp



app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = config["JWT_SECRET_KEY"]
jwt = JWTManager(app)

app.register_blueprint(auth_bp)
