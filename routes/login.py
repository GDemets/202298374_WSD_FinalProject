from flask import request, jsonify, redirect
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token,jwt_required, get_jwt_identity, get_jwt
from error_response import error_response
from models import User, db
from dto.user_dto import UserCreateDTO, UserUpdateDTO
from marshmallow import ValidationError
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from dotenv import load_dotenv
from firebase_admin import auth

import urllib.parse
import requests
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
    
    @app.route("/login/google", methods=["GET"])
    def login_google_redirect():
        """
        Redirect user to Google OAuth login
        ---
        tags:
          - Authentification
        responses:
          302:
            description: Redirect to Google login page
        """
        params = {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "redirect_uri": "http://localhost:5000/login/google/callback",
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent"
        }
        url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
        return redirect(url)

    @app.route("/login/google/callback", methods=["GET"])
    def login_google_callback():
        code = request.args.get("code")
        if not code:
            return "Missing code", 400

        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "redirect_uri": "http://localhost:5000/login/google/callback",
            "grant_type": "authorization_code"
        }

        r = requests.post(token_url, data=data)
        token_response = r.json()

        # Récupération du id_token pour l'API POST
        id_token_value = token_response.get("id_token")
        if not id_token_value:
            return jsonify({"error": "Failed to obtain id_token"}), 400

        # Vérifie le token et crée l'utilisateur comme dans ton POST
        try:
            idinfo = id_token.verify_oauth2_token(
                id_token_value,
                google_requests.Request(),
                audience=os.getenv("GOOGLE_CLIENT_ID")
            )
        except ValueError:
            return error_response(401, "INVALID_GOOGLE_TOKEN", "Invalid Google token")

        email = idinfo.get("email")
        if not idinfo.get("email_verified"):
            return error_response(401, "EMAIL_NOT_VERIFIED", "Google email not verified")

        user = User.query.filter_by(mail=email).first()
        if not user:
            pseudo = email.split("@")[0]
            user = User(
                pseudo=pseudo,
                mail=email,
                role="user",
                password_hash="1234" #
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
            "id_token": id_token_value,
            "message": "Login with Google successful"
        }), 200
        
    @app.route('/login/firebase', methods=['POST'])
    def login_firebase():
        """
        Login with Firebase (Google, Facebook, Apple...)
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
                idToken:
                  type: string
                  example: "eyJhbGciOiJSUzI1NiIs..."
              required:
                - idToken
        responses:
            200:
                description: User successfully connected with Firebase
            400:
                description: Invalid request
            401:
                description: Invalid Firebase token
        """
        data = request.get_json()
        if not data or "idToken" not in data:
            return error_response(
                status=400,
                code="INVALID_QUERY_PARAM",
                message="idToken is required"
            )

        try:
            # 🔐 Vérification du token Firebase
            decoded_token = auth.verify_id_token(data["idToken"])

            firebase_uid = decoded_token["uid"]
            email = decoded_token.get("email")
            name = decoded_token.get("name", "")

        except Exception:
            return error_response(
                status=401,
                code="INVALID_FIREBASE_TOKEN",
                message="Invalid Firebase token"
            )

        # 🔍 Vérifier si user existe
        user = User.query.filter_by(mail=email).first()

        if not user:
            pseudo = email.split("@")[0] if email else f"user_{firebase_uid[:6]}"

            user = User(
                pseudo=pseudo,
                mail=email,
                role="user",
                password_hash="firebase_auth"
            )
            db.session.add(user)
            db.session.commit()

        # 🔑 Générer TES tokens JWT
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role}
        )

        refresh_token = create_refresh_token(identity=str(user.id))

        return jsonify({
            "status": "success",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "message": "Login with Firebase successful"
        }), 200


