from flask import Flask, jsonify, request
from flasgger import Swagger
from models import db
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from datetime import timedelta
from routes.user import users_routes
from routes.login import login_routes
from routes.post import posts_routes
from routes.category import category_routes
from routes.comment import comment_routes
from routes.favorite import favorite_routes

from datetime import datetime

import logging
import os

import firebase_admin
from firebase_admin import credentials

if not firebase_admin._apps:
    cred = credentials.Certificate("wsd-termproject-fa20d-firebase-adminsdk-fbsvc-295bb91beb.json")
    firebase_admin.initialize_app(cred)

### Flask App and Database Configuration ###
load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY")
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)

db.init_app(app)
jwt = JWTManager(app)
swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "Blog API",
        "description": "API documentation",
    },
    "securityDefinitions": {
        "BearerAuth": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Add 'Bearer <your_token>'"
        }
    }
})

def create_tables():
    db.create_all()

@app.before_request
def ensure_tables_exist():
    if not app.config.get("TESTING", False):
        create_tables()
        
### Middleware to log requests ###
@app.before_request
def log_request_info():
    logging.info(f"{datetime.now().isoformat()} - {request.method} {request.path}")

### Routes ###
@app.route('/health', methods=['GET'])
def health_check():
    response_data = {
      "status": "UP",
      "service": "Bookstore-api",
      "timestamp": datetime.now().isoformat(),
    }
    return jsonify(response_data), 200

@app.route('/')
def index():
    from flask import redirect
    return redirect('/apidocs/')

users_routes(app)
login_routes(app)
posts_routes(app)
category_routes(app)
comment_routes(app)
favorite_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
