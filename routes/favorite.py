from flask import request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token,jwt_required, get_jwt_identity, get_jwt
from error_response import error_response
from models import Comment, User, Post, Favorite, db
from dto.user_dto import UserCreateDTO, UserUpdateDTO
from marshmallow import ValidationError

def favorite_routes(app):
    
    ### GET ###
    @app.route('/favorites/me', methods=['GET'])
    @jwt_required(optional=True)
    def get_favorites():
        """
        Get favorites for connected user
        ---
        tags:
          - Favorites
        security:
          - BearerAuth: []
        responses:
          200:
            description: Favorites successfully retrieved
          401:
            description: Unauthorized
        """
        current_user_id = get_jwt_identity()
        if current_user_id is None:
            return error_response(status=401,code='UNAUTHORIZED',message='No authentication token or invalid token')
        favorites = Favorite.query.filter_by(user_id=current_user_id).all()

        return jsonify({
            'status': 'success',
            'message': 'Favorites successfully retrieved',
            'data': [fav.to_dict() for fav in favorites]
        }), 200

    @app.route('/favorites/posts/<int:post_id>/users', methods=['GET'])
    @jwt_required(optional=True)
    def get_users_by_favorite_post(post_id):
        """
        Get all users who have this post in their favorites
        ---
        tags:
         - Favorites
        security:
         - BearerAuth: []
        parameters:
          - name: post_id
            in: path
            required: true
            type: integer
        responses:
          200:
            description: Users successfully retrieved
          403:
            description: Forbidden
          404:
            description: Post not found
        """
        claims = get_jwt()
        if claims.get("role") != "admin":
            return error_response(status=403,code='FORBIDDEN',message='No access')

        post = Post.query.get(post_id)
        if not post:
            return error_response(tatus=404,code='RESSOURCE_NOT_FOUND',message='Post ID does not exist')

        favorites = Favorite.query.filter_by(post_id=post_id).all()
        users = [User.query.get(fav.user_id).to_dict() for fav in favorites]

        return jsonify({
            'status': 'success',
            'message': 'Users successfully retrieved',
            'data': users
        }), 200
    
    ### POST ###
    @app.route('/favorites/<int:post_id>', methods=['POST'])
    @jwt_required(optional=True)
    def add_to_favorites(post_id):
        """
        Add a post to the user's favorites
        ---
        tags:
          - Favorites
        security:
          - BearerAuth: []
        parameters:
          - name: post_id
            in: path
            required: true
            type: integer
        responses:
          201:
            description: Post successfully added to favorites
          400:
            description: Post already in favorites
          401:
            description: No authentication token or invalid token
          404:
            description: User or post not found
          500:
            description: Internal servor error
        """
        current_user_id = get_jwt_identity()
        if current_user_id is None:
            return error_response(status=401,code='UNAUTHORIZED',message='No authentication token or invalid token')
        
        user = User.query.get(current_user_id)
        if not user:
            return error_response(status=404,code='USER_NOT_FOUND',message='User ID does not exist')

        post = Post.query.get(post_id)
        if not post:
            return error_response(status=404,code='RESSOURCE_NOT_FOUND',message='Post ID does not exist')

        existing = Favorite.query.filter_by(
            user_id=current_user_id,
            post_id=post_id
        ).first()

        if existing:
            return error_response(
                status=400,
                code='STATE_CONFLICT',
                message='Post already in favorites'
            )

        favorite = Favorite(
            user_id=current_user_id,
            post_id=post_id
        )

        try:
            db.session.add(favorite)
            db.session.commit()
        except Exception as e:
            print(e)
            return error_response(
                status=500,
                code='INTERNAL_SERVER_ERROR',
                message='Internal server error'
            )

        return jsonify({
            'status': 'success',
            'message': 'Post successfully added to favorites',
            'data': favorite.to_dict()
        }), 201

    ### DELETE ###
    @app.route('/favorites/<int:post_id>', methods=['DELETE'])
    @jwt_required(optional=True)
    def delete_favorite(post_id):
        """
        Remove a post from favorites
        ---
        tags:
          - Favorites
        security:
          - BearerAuth: []
        parameters:
          - name: post_id
            in: path
            required: true
            type: integer
        responses:
          200:
            description: Favorite successfully deleted
          404:
            description: Favorite not found
        """
        current_user_id = get_jwt_identity()
        if current_user_id is None:
            return error_response(status=401,code='UNAUTHORIZED',message='No authentication token or invalid token')

        favorite = Favorite.query.filter_by(post_id=post_id,user_id=current_user_id).first()
        if not favorite:
            return error_response(status=404,code='RESSOURCE_NOT_FOUND',message='Favorite does not exist')

        try:
            db.session.delete(favorite)
            db.session.commit()
        except Exception as e:
            print(e)
            return error_response(status=500,code='INTERNAL_SERVER_ERROR',message='Internal server error')

        return jsonify({
            'status': 'success',
            'message': 'Favorite successfully deleted'
        }), 200
