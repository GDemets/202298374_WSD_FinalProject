from flask import request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token,jwt_required, get_jwt_identity, get_jwt
from error_response import error_response
from models import User, db
from dto.user_dto import UserCreateDTO, UserUpdateDTO
from marshmallow import ValidationError
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from dotenv import load_dotenv


import os
load_dotenv()

def login_routes(app):

    ### User Login ###
    @app.route('/login', methods=['POST'])
    def login():
        """
        Log a user
        ---
        tags:
          - Authentification
        consumes:
          - application/json
        parameters:
          - in: body
            name: body
            required: true
            schema: 
              type: object
              properties:
                mail:
                  type: string
                  example: "alice@mail.com"
                password:
                  type: string
                  example: "1234"
              required:
                - mail
                - password
        responses:
            200:
                description: Users successfully connected
            400:
                description: Missing mail or password
            401:
                description: Invalid password
        """
        data = request.get_json()
        if not request.json :
            return error_response(status=400,code='BAD_REQUEST',message='The request is not formatted correctly')
        if 'mail' not in request.json or 'password' not in request.json :
            return error_response(status=400,code='INVALID_QUERY_PARAM',message='Invalid query parameter value')

        user = User.query.filter_by(mail=data["mail"]).first()
        if user is None:
            return error_response(status=404,code='USER_NOT_FOUND',message='User does not exist')

        if not user.check_password(data["password"]):
            return error_response(status=401,code='INVALID_CREDENTIALS',message='Invalid mail or password')

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role}
        )

        refresh_token = create_refresh_token(identity=str(user.id))

        return jsonify({
            'status': 'success',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'message': 'Login successful'
        }), 200
    
    @app.route("/refresh", methods=["POST"])
    @jwt_required(optional=True)
    def refresh():
        """
        Refresh access token
        ---
        tags:
          - Authentification
        security:
          - BearerAuth: []
        responses:
            200:
              description: Acces token refresh successfully
            400:
              description: Missing mail or password
            401:
              description: Missing or invalide token
        """
        current_user_id = get_jwt_identity()
        if current_user_id is None:
            return error_response(status=401,code='UNAUTHORIZED',message='No authentication token or invalid token')

        new_access_token = create_access_token(
            identity=current_user_id
        )

        return jsonify({
            "status": "success",
            "access_token": new_access_token,
            "message": "Access token successfully refreshed"
        }), 200
    
  

    @app.route('/login/google', methods=['POST'])
    def login_google():
        """
        Login with Google
        ---
        tags:
          - Authentification
        consumes:
          - application/json
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              properties:
                id_token:
                  type: string
                  example: "eyJhbGciOiJSUzI1NiIs..."
              required:
                - id_token
        responses:
            200:
                description: User successfully connected with Google
            400:
                description: Invalid request
            401:
                description: Invalid Google token
        """
        data = request.get_json()
        if not data or "id_token" not in data:
            return error_response(status=400,code="INVALID_QUERY_PARAM",message="id_token is required")

        try:
            idinfo = id_token.verify_oauth2_token(
                data["id_token"],
                google_requests.Request(),
                audience=os.getenv("GOOGLE_CLIENT_ID")
            )

            email = idinfo.get("email")
            email_verified = idinfo.get("email_verified")

            if not email_verified:
                return error_response(
                    status=401,
                    code="EMAIL_NOT_VERIFIED",
                    message="Google email not verified"
                )

        except ValueError:
            return error_response(
                status=401,
                code="INVALID_GOOGLE_TOKEN",
                message="Invalid Google token"
            )

        user = User.query.filter_by(mail=email).first()
        pseudo = email.split("@")[0]  

        user = User(
            pseudo=pseudo,
            mail=email,
            role="user",
            password_hash="1234"
        )
        db.session.add(user)
        db.session.commit()

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role}
        )

        refresh_token = create_refresh_token(identity=str(user.id))

        return jsonify({
            "status": "success",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "message": "Login with Google successful"
        }), 200

