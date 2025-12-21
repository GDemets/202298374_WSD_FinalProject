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
from extensions import cache

import logging
import os

load_dotenv()

### Flask App and Database Configuration ###
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY")
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 60

cache.init_app(app)
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
    """
    Health Check
    ---
    tags:
      - Health
    responses:
      200:
        description: Service is healthy
        schema:
          type: object
          properties:
            status:
              type: string
              example: UP
            service:
              type: string
              example: Bookstore-api
            version:
              type: string
              example: 1.0.0
            timestamp:
              type: string
              example: 2025-01-01T12:00:00Z
    """
    return jsonify({
        "status": "UP",
        "service": "Bookstore-api",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }), 200

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

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=3000
    )