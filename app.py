from flask import Flask, request, jsonify, abort, render_template
from flasgger import Swagger
from models import db, User, Post, Comment, Category
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token,jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
from dotenv import load_dotenv
from datetime import timedelta, datetime
from error_response import error_response
from routes.user import users_routes
from routes.login import login_routes
from routes.post import posts_routes
from routes.category import category_routes
from routes.comment import comment_routes
import logging
import os

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY")
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
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

db.init_app(app)
jwt = JWTManager(app)

users_routes(app)
login_routes(app)
posts_routes(app)
category_routes(app)
comment_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
