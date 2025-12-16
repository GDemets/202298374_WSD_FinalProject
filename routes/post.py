from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import Post,Category, db
from error_response import error_response
from dto.user_dto import UserCreateDTO, UserUpdateDTO
from marshmallow import ValidationError

def posts_routes(app):

    ### GET POSTS ###
    @app.route('/posts', methods=['GET'])
    def get_posts():
        """
        Get all the posts.
        ---
        tags:
            - Posts
        parameters:
          - in: query
            name: page
            type: page
            type: integer
            required: false
            default: 1
          - in: query
            name: limit
            type: integer
            required: false
            default: 10
        responses:
            200:
                description: Posts successfully retrieved.
        """
        try:
            page = request.args.get('page', 1, type=int)
            limit = request.args.get('limit', 10, type=int)

            if page < 1 or limit < 1:
                return error_response(
                    status=400,
                    code='INVALID_QUERY_PARAM',
                    message='Page and limit must be positive integers'
                )

            pagination = Post.query.order_by(Post.created_at.desc()).paginate(
                page=page,
                per_page=limit,
                error_out=False
            )

            posts = pagination.items

            return jsonify({
                'status': 'success',
                'message': 'Posts successfully retrieved',
                'data': [post.to_dict() for post in posts],
                'pagination': {
                    'page': pagination.page,
                    'limit': limit,
                    'total_pages': pagination.pages,
                    'total_items': pagination.total,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }), 200
        except Exception as e:
            print(e)
            return error_response(
                status=500,
                code='INTERNAL_SERVER_ERROR',
                message='Internal server error'
            )

    @app.route('/posts/<int:post_id>', methods=['GET'])
    def get_post(post_id):
        """
        Get a post by its ID
        ---
        tags:
          - Posts
        parameters:
          - name: post_id
            in: path
            required: true
            type: integer
        responses:
          200:
            description: Post successfully retrieved
          404:
            description: Post not found
        """
        post = Post.query.get(post_id)
        if not post:
            return error_response(
                status=404,
                code='RESSOURCE_NOT_FOUND',
                message='Post ID does not exist'
            )

        return jsonify({
            'status': 'success',
            'message': 'Post successfully retrieved',
            'data': post.to_dict()
        }), 200

    @app.route('/posts/category', methods=['GET'])
    def get_posts_by_category():
        """
        Get all posts filtered by category name
        ---
        tags:
          - Posts
        parameters:
          - in: query
            name: category
            required: true
            type: string
            example: Technology
        responses:
          200:
            description: List of posts
          400:
            description: Missing category query parameter
        """
        category = request.args.get('category')

        if not category:
            return error_response(
                status=400,
                code='MISSING_QUERY_PARAM',
                message='Category query parameter is required'
            )

        try:
            posts = (
                Post.query
                .join(Category)
                .filter(Category.name.ilike(f"%{category}%"))
                .all()
            )
        except Exception as e:
            print(e)
            return error_response(
                status=500,
                code='INTERNAL_SERVER_ERROR',
                message='Internal server error'
            )

        if not posts:
            return error_response(
                status=404,
                code='NOT_FOUND',
                message='No posts found for this category'
            )

        return jsonify({
            'status': 'success',
            'message': 'Posts successfully retrieved',
            'data': [post.to_dict() for post in posts]
        }), 200
    
    @app.route('/posts/search', methods=['GET'])
    def search_posts():
        """
        Search posts by multiple criteria with pagination
        ---
        tags:
          - Posts
        parameters:
          - in: query
            name: title
            type: string
            required: false
          - in: query
            name: content
            type: string
            required: false
          - in: query
            name: category
            type: string
            required: false
          - in: query
            name: user_id
            type: integer
            required: false
          - in: query
            name: page
            type: integer
            default: 1
          - in: query
            name: limit
            type: integer
            default: 10
        responses:
          200:
            description: Paginated list of posts
          400: 
            description: Page and limit must be positive integers
          500:
            description: Internal server error
        """
        try:
            title = request.args.get('title', type=str)
            content = request.args.get('content', type=str)
            category_name = request.args.get('category', type=str)
            user_id = request.args.get('user_id', type=int)
            page = request.args.get('page', 1, type=int)
            limit = request.args.get('limit', 10, type=int)

            if page < 1 or limit < 1:
                return error_response(
                    status=400,
                    code='INVALID_QUERY_PARAM',
                    message='Page and limit must be positive integers'
                )
            query = Post.query
            if title:
                query = query.filter(Post.title.ilike(f"%{title}%"))
            if content:
                query = query.filter(Post.content.ilike(f"%{content}%"))
            if category_name:
                query = query.join(Category).filter(Category.name.ilike(f"%{category_name}%"))
            if user_id:
                query = query.filter(Post.user_id == user_id)

            pagination = query.paginate(page=page, per_page=limit, error_out=False)

            return jsonify({
                'status': 'success',
                'message': 'Posts successfully retrieved',
                'data': [post.to_dict() for post in pagination.items],
                'pagination': {
                    'page': pagination.page,
                    'limit': limit,
                    'total_pages': pagination.pages,
                    'total_items': pagination.total,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }), 200

        except Exception as e:
            print(e)
            return error_response(status=500,code='INTERNAL_SERVER_ERROR',message='Internal server error')
    
    ### POST ###
    @app.route('/posts', methods=['POST'])
    @jwt_required(optional=True)
    def create_post():
        """
        Create a new post
        ---
        tags:
          - Posts
        security:
          - BearerAuth: []
        parameters:
          - in: body
            name: body
            required: true
            description: Post data
            schema:
              type: object
              required:
                - title
                - content
                - category_id
              properties:
                title:
                  type: string
                  example: "Title post"
                content:
                  type: string
                  example: "Content"
                category_id:
                  type: integer
                  example: 1
        responses:
          201:
            description: Posts correctly posted
          400: 
            description: Missing required fields or format invaid
          401:
            description: Missing token no access
          500:
            description: Internal server error
        """
        current_user_id = get_jwt_identity()
        if current_user_id is None:
          return error_response(status=401,code='UNAUTHORIZED',message='No authentication token or invalid token')

        required_fields = ['title', 'content', 'category_id']

        if not request.json:
            return error_response(status=400, code='BAD_REQUEST', message='Invalid JSON')
        if not all(field in request.json for field in required_fields):
            return error_response(status=400, code='INVALID_QUERY_PARAM', message='Missing required fields')

        post = Post(
            title=request.json['title'],
            content=request.json['content'],
            category_id=request.json['category_id'],
            user_id=current_user_id
        )

        try:
            db.session.add(post)
            db.session.commit()
        except Exception as e:
            print(e)
            return error_response(status=500, code='INTERNAL_SERVER_ERROR', message='Internal server error')

        return jsonify({'status': 'success','message': 'Post successfully created','data': post.to_dict()}), 201
    
    @app.route('/posts/<int:post_id>', methods=['PUT'])
    @jwt_required()
    def update_post(post_id):
        """
        Update a post
        ---
        tags:
          - Posts
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
            description: Post data
            schema:
              type: object
              required:
                - title
                - content
                - category_id
              properties:
                title:
                  type: string
                  example: "New title post"
                content:
                  type: string
                  example: "New content"
                category_id:
                  type: integer
                  example: 2
        responses:
          200:
            description: Post successfully updated
          403:
            description: Forbidden
          404:
            description: Post does not exist
        """
        current_user_id = int(get_jwt_identity())
        if current_user_id is None:
            return error_response(status=401,code='UNAUTHORIZED',message='No authentication token or invalid token')

        post = Post.query.get(post_id)
        if not post:
            return error_response(status=404,code='RESSOURCE_NOT_FOUND',message='Post ID does not exist')
        
        if post.user_id != current_user_id:
          print("cvbn",post.user_id,current_user_id)
          return error_response(status=403,code='FORBIDDEN',message='You are not allowed to modify this post')

        if not request.json:
            return error_response(status=400,code='BAD_REQUEST',message='Invalid JSON')

        try:
            post.title = request.json.get('title', post.title)
            post.content = request.json.get('content', post.content)
            post.category_id = request.json.get('category_id', post.category_id)
            db.session.commit()
        except Exception as e:
            print(e)
            return error_response(status=500,code='INTERNAL_SERVER_ERROR',message='Internal server error')

        return jsonify({
            'status': 'success',
            'message': 'Post successfully updated',
            'data': post.to_dict()
        }), 200


    ### DELETE ###
    @app.route('/posts/<int:post_id>', methods=['DELETE'])
    @jwt_required(optional=True)
    def delete_post(post_id):
        """
        Delete a post
        ---
        tags:
          - Posts
        security:
          - BearerAuth: []
        parameters:
          - name: post_id
            in: path
            required: true
            schema:
              type: integer
        responses:
          200:
            description: Post successfully deleted
          403:
            description: Only admin can delete posts
          404:
            description: Post does not exist
        """
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        role = claims.get("role")

        if current_user_id is None:
            return error_response(status=401,code='UNAUTHORIZED',message='Authentication required')
        
        current_user_id=int(current_user_id)

        post = Post.query.get(post_id)
        if not post:
            return error_response(status=404,code='RESSOURCE_NOT_FOUND',message='Post ID does not exist')
        
        if role != "admin" and post.user_id != current_user_id:
            return error_response(status=403,code='FORBIDDEN',message='You are not allowed to delete this post')

        try:
            db.session.delete(post)
            db.session.commit()
        except Exception as e:
            print(e)
            return error_response(status=500,code='INTERNAL_SERVER_ERROR',message='Internal server error')

        return jsonify({
            'status': 'success',
            'message': 'Post successfully deleted'
        }), 200