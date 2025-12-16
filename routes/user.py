from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import User, db
from error_response import error_response
from dto.user_dto import UserCreateDTO, UserUpdateDTO
from marshmallow import ValidationError

def users_routes(app):

    ### GET ###
    @app.route('/users', methods=['GET'])
    def get_users():
        """
        Get all the users.
        ---
        tags:
            - Users
        responses:
            200:
                description: Users successfully retrieved.
                schema:
                type: object
                properties:
                    message:
                    type: string
        """
        try:
            users = User.query.all()
        except Exception as e:
            print(e)
            return error_response(500, 'INTERNAL_SERVER_ERROR', 'Internal server error')

        return jsonify({
            'status': 'success',
            'message': 'Users successfully retrieved',
            'data': [user.to_dict() for user in users]
        }), 200

    @app.route('/users/me', methods=['GET'])
    @jwt_required(optional=True)
    def get_me():
        """
        Get informations of a connected user.
        ---
        tags:
            - Users
        security:
            - BearerAuth []
        responses:
            200:
                description: Users successfully retrieved.
                schema:
                type: object
                properties:
                    message:
                    type: string
            401:
                description: No authentication token or invalid token.
                schema:
                type: object
                properties:
                    message:
                    type: string
            404:
                description: User not found.
                schema:
                type: object
                properties:
                    message:
                    type: string
        """
        current_user_id = get_jwt_identity()
        if current_user_id is None:
            return error_response(401, 'UNAUTHORIZED', 'No authentication token or invalid token')

        user = User.query.get(current_user_id)
        if not user:
            return error_response(404, 'USER_NOT_FOUND', 'User ID does not exist')

        return jsonify({
            'status': 'success',
            'message': 'User successfully retrieved',
            'data': user.to_dict()
        }), 200
    
    ### POST ###
    @app.route('/users', methods=['POST'])
    def create_user():
        """
        Create a new user
        ---
        tags:
            - Users
        consumes:
            - application/json
        parameters:
        - in: body
          name: body
          required: true
          description: User information to create
          schema:
            type: object
            required:
                - pseudo
                - mail
                - password
            properties:
                pseudo:
                  type: string
                  example: johndoe
                mail:
                  type: string
                  example: johndoe@example.com
                password:
                  type: string
                  example: mysecretpassword
        responses:
          201:
            description: User successfully created
          400:
            description: Missing or invalid fields
          409:
            description: User already exists
        """
        if not request.json :
            return error_response(status=400,code='BAD_REQUEST',message='The request is not formatted correctly')
        if 'pseudo' not in request.json or 'mail' not in request.json or 'password' not in request.json:
            return error_response(status=400,code='INVALID_QUERY_PARAM',message='Invalid query parameter value')

        schema = UserCreateDTO()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return error_response(status=400,code='VALIDATION_FAILED',message='Field validation failed')
        
        user = User(
            pseudo=data['pseudo'],
            mail=data['mail'],
            role="user" #set user role as default
        )
        user.set_password(data['password'])
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            print(e)
            return error_response(status=409,code='DUPLICATE_RESSOURCE',message='Data already exists')
        
        return jsonify({
            'status': 'success',
            'message': 'User successfully created',
            'data': user.to_dict()
        }), 201
    
    ### PUT ###
    @app.route('/users/me', methods=['PUT'])
    @jwt_required(optional=True)
    def update_user():
        """
        Update a new user information
        ---
        tags:
            - Users
        security:
            - BearerAuth: []
        consumes:
            - application/json
        parameters:
        - in: body
          name: body
          required: true
          description: Information to update
          schema:
            type: object
            required:
                - pseudo
                - mail
                - password
            properties:
                pseudo:
                  type: string
                  example: NewPseudo
                mail:
                  type: string
                  example: new@example.com
                password:
                  type: string
                  example: 1234
        responses:
          200:
            description: User information successfully updated
          400:
            description: Missing or invalid fields
          403:
            description: Unauthorized action
          409:
            description: Missing or invalid fields
        """
        current_user_id = get_jwt_identity()
        if current_user_id is None:
            return error_response(status=401,code='UNAUTHORIZED',message='No authentication token or invalid token')
        if not request.json :
            return error_response(status=400,code='BAD_REQUEST',message='The request is not formatted correctly')
        if 'mail' not in request.json :
            return error_response(status=400,code='INVALID_QUERY_PARAM',message='Invalid query parameter value')
        
        schema = UserUpdateDTO()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return error_response(status=400,code='VALIDATION_FAILED',message='Field validation failed')
        
        try:
            user = User.query.get(current_user_id)
            user.pseudo = data['pseudo']
            user.mail = data['mail']
            if 'password' in request.json:
                user.set_password(data['password'])
            db.session.commit()
        except Exception as e:
            print(e)
            return error_response(status=404,code='USER_NOT_FOUND',message='User ID does not exist')

        return jsonify({
            'status': 'success',
            'message': 'User successfully modified',
            'data': user.to_dict()
        }), 200
    
    ### PATCH ###
    @app.route('/users/<int:user_id>/make_admin', methods=['PATCH'])
    @jwt_required()
    def make_user_admin(user_id):
        """
        Promote a user to admin (only admin)
        ---
        tags:
            - Users
        security:
            - BearerAuth: []
        parameters:
        - name: user_id
          in: path
          required: true
          description: Id of the user to promote
        responses:
          200:
            description: User promoted to admin successfully
          403:
            description: Forbidden, only admin can promote
          404:
            description: User not found
          500:
            description: Error while updating user
        """
        claims = get_jwt()
        if claims.get("role") != "admin":
            return error_response(status=403,code='FORBIDDEN',message='No access')
        
        user_to_promote = User.query.get(user_id)
        if not user_to_promote:
            return error_response(status=404,code='USER_NOT_FOUND',message='User ID does not exist')

        if user_to_promote.role == 'admin':
            return error_response(status=409,code='STATE_CONFLICT',message='Resource state conflict: already admin')

        try:
            user_to_promote.role = 'admin'
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print("Error promoting user:", e)
            return error_response(status=500,code='INTERNAl_SERVER_ERROR',message='Internal server error')

        return jsonify({
            'status': 'success',
            'message': f'User {user_to_promote.pseudo} has been promoted to admin',
            'user': user_to_promote.to_dict()
        }), 200
    
    ### DELETE ###
    @app.route('/users/me', methods=['DELETE'])
    @jwt_required(optional=True)
    def delete_user():
        """
        Delete a connected user
        ---
        tags:
            - Users
        security:
            - BearerAuth: []
        responses:
          200:
            description: User deleted successfully
          404:
            description: User not found
        """
        current_user_id = get_jwt_identity()
        if current_user_id is None:
            return error_response(status=401,code='UNAUTHORIZED',message='No authentication token or invalid token')
        
        try:
            user = User.query.get(current_user_id)
            db.session.delete(user)
            db.session.commit()
        except Exception as e:
            print(e)
            return error_response(status=404,code='USER_NOT_FOUND',message='User ID does not exist')

        return jsonify({'status': 'success', 'message': 'User successfully deleted'}), 200