from flask import request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token,jwt_required, get_jwt_identity, get_jwt
from error_response import error_response
from models import Comment, User, Post, db
from dto.user_dto import UserCreateDTO, UserUpdateDTO
from marshmallow import ValidationError

def comment_routes(app):

    ### GET ###
    @app.route('/comments/me', methods=['GET'])
    @jwt_required(optional=True)
    def get_comments_user():
        """
        Get all comments for connected user
        ---
        tags:
          - Comments
        security:
          - BearerAuth: []
        responses:
          200:
            description: Comments successfully retrieved
          401:
            description: Unauthorized
        """
        current_user_id = get_jwt_identity()
        if current_user_id is None:
            return error_response(status=401,code="UNAUTHORIZED",message="Authentication required")
        current_user_id = int(current_user_id)

        comments = Comment.query.filter_by(user_id=current_user_id).all()
        return jsonify({
            'status': 'success',
            'message': 'Comments successfully retrieved',
            'data': [comment.to_dict() for comment in comments]
        }), 200
    
    @app.route('/posts/<int:post_id>/comments', methods=['GET'])
    def get_comments_post(post_id):
        """
        Get all comments related to a specific post
        ---
        tags:
          - Comments
        parameters:
          - name: post_id
            in: path
            required: true
            type: integer
        responses:
          200:
            description: Comments successfully retrieved
          404:
            description: Post not found
          500:
            description: Internal servor error
        """
        try:
            post = Post.query.get(post_id)
        except Exception as e:
            print(e)
            return error_response(status=500,code='INTERNAL_SERVER_ERROR',message='Internal server error')
        if not post:
            return error_response(status=404,code='RESSOURCE_NOT_FOUND',message='Post ID does not exist')

        comments = Comment.query.filter_by(post_id=post_id).all()

        return jsonify({
            'status': 'success',
            'message': 'Comments successfully retrieved',
            'data': [comment.to_dict() for comment in comments]
        }), 200

    
    ### POST ###
    @app.route('/posts/<int:post_id>/comments', methods=['POST'])
    @jwt_required(optional=True)
    def create_comment(post_id):
        """
        Create a new comment for a specific post
        ---
        tags:
          - Comments
        security:
          - BearerAuth: []
        parameters:
          - name: post_id
            in: path
            required: true
            type: integer
          - in: body
            name: body
            required: true
            description: New comment data
            schema:
              type: object
              properties:
                content:
                  type: string
                  example: "Great post!"
              required:
                - content
        responses:
          201:
            description: Comment successfully created
          400:
            description: Invalid JSON
          404:
            description: Post not found
          500:
            description: Internal servor error
        """
        current_user_id = get_jwt_identity()
        if current_user_id is None:
            return error_response(status=401,code='UNAUTHORIZED',message='No authentication token or invalid token')
        current_user_id=int(current_user_id)

        if not request.json or 'content' not in request.json:
            return error_response(status=400,code='INVALID_QUERY_PARAM',message='Content is required')

        post = Post.query.get(post_id)
        if not post:
            return error_response(status=404,code='RESSOURCE_NOT_FOUND',message='Post ID does not exist')
        
        comment = Comment(
            content=request.json['content'],
            user_id=current_user_id,
            post_id=post_id
        )

        try:
            db.session.add(comment)
            db.session.commit()
        except Exception as e:
            print(e)
            return error_response(status=500,code='INTERNAL_SERVER_ERROR',message='Internal server error')

        return jsonify({
            'status': 'success',
            'message': 'Comment successfully created',
            'data': comment.to_dict()
        }), 201

    ### PUT ###
    @app.route('/comments/<int:comment_id>', methods=['PUT'])
    @jwt_required(optional=True)
    def update_comment(comment_id):
        """
        Update an existing comment
        ---
        tags:
          - Comments
        security:
          - BearerAuth: []
        parameters:
          - name: comment_id
            in: path
            required: true
            type: integer
          - in: body
            name: body
            required: true
            description: New comment data
            schema:
              type: object
              properties:
                content:
                  type: string
                  example: "New post!"
              required:
                - content
        responses:
          200:
            description: Comment successfully updated
          400:
            description: Invalid JSON
          403:
            description: Unauthorized to updated this comment
          404:
            description: Post not found
          500:
            description: Internal servor error
        """
        claims = get_jwt()
        current_user_id = get_jwt_identity()
        role = claims.get("role")
        comment = Comment.query.get(comment_id)

        if current_user_id is None:
            return error_response(status=401,code='UNAUTHORIZED',message='No authentication token or invalid token')
        current_user_id=int(current_user_id)

        comment = Comment.query.get(comment_id)
        if not comment:
            return error_response(status=404,code='RESSOURCE_NOT_FOUND',message='Comment ID does not exist')
        if comment.user_id != current_user_id:
            return error_response(status=403,code='FORBIDDEN',message='You are not allowed to delete this comment')
        if not request.json or 'content' not in request.json:
            return error_response(status=400,code='INVALID_QUERY_PARAM',message='Content is required')
        
        try:
            comment.content = request.json['content']
            db.session.commit()
        except Exception as e:
            print(e)
            return error_response(status=500,code='INTERNAL_SERVER_ERROR',message='Internal server error')

        return jsonify({
            'status': 'success',
            'message': 'Comment successfully updated',
            'data': comment.to_dict()
        }), 200

    ### DELETE ###
    @app.route('/comments/<int:comment_id>', methods=['DELETE'])
    @jwt_required(optional=True)
    def delete_comment(comment_id):
        """
        Delete a comment by ID
        ---
        tags:
          - Comments
        security:
          - BearerAuth: []
        parameters:
          - name: comment_id
            in: path
            required: true
            type: integer
        responses:
          200:
            description: Comment successfully updated
          400:
            description: Invalid JSON
          403:
            description: Unauthorized to deleted this comment
          404:
            description: Post not found
          500:
            description: Internal servor error
        """       
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        role = claims.get("role")

        if current_user_id is None:
            return error_response(status=401,code='UNAUTHORIZED',message='Authentication required')
        
        current_user_id=int(current_user_id)

        comment = Comment.query.get(comment_id)
        if not comment:
            return error_response(status=404,code='RESSOURCE_NOT_FOUND',message='Post ID does not exist')
        
        if role != "admin" and comment.user_id != current_user_id:
            return error_response(status=403,code='FORBIDDEN',message='You are not allowed to delete this post')

        try:
            db.session.delete(comment)
            db.session.commit()
        except Exception as e:
            print(e)
            return error_response(status=500,code='INTERNAL_SERVER_ERROR',message='Internal server error')

        return jsonify({
            'status': 'success',
            'message': 'Comment successfully deleted'
        }), 200

