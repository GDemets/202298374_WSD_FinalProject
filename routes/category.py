from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from error_response import error_response
from models import Category, db

def category_routes(app):

    ### GET ###
    @app.route('/categories', methods=['GET'])
    def get_categories():
        """
        Get all categories
        ---
        tags:
          - Categories
        responses:
          200:
            description: List of all categories
        """
        try:
            categories = Category.query.all()
        except Exception as e:
            print(e)
            return error_response(
                status=500,
                code='INTERNAL_SERVER_ERROR',
                message='Internal server error'
            )

        return jsonify({
            'status': 'success',
            'message': 'Categories successfully retrieved',
            'data': [cat.to_dict() for cat in categories]
        }), 200
    
    @app.route('/categories/<int:cat_id>', methods=['GET'])
    def get_category(cat_id):
        """
        Get a category by its ID
        ---
        tags:
          - Categories
        parameters:
          - in: path
            name: cat_id
            required: true
            type: integer
        responses:
          200:
            description: Category successfully retrieved
          404:
            description: Category not found
        """
        cat = Category.query.get(cat_id)
        if not cat:
            return error_response(
                status=404,
                code='RESSOURCE_NOT_FOUND',
                message='Category ID does not exist'
            )

        return jsonify({
            'status': 'success',
            'message': 'Category successfully retrieved',
            'data': cat.to_dict()
        }), 200

    @app.route('/categories', methods=['POST'])
    @jwt_required(optional=True)
    def create_category():
        """
        Create a new category
        ---
        tags:
          - Categories
        security:
          - BearerAuth: []
        parameters:
          - in: body
            name: Category data
            required: true
            schema:
              type: object
              required: true
                - name
              properties:
                name:
                  type: string
                  example: "Computer Science"
        responses:
          201:
            description: Category successfully created
          400:
            description: Invalid or missing data
          404:
            description: Category not found
          409:
            description: Conflict, category already exists
        """
        claims = get_jwt()
        if claims.get("role") != "admin":
            return error_response(
                status=403,
                code='FORBIDDEN',
                message='No access'
            )

        if not request.json or 'name' not in request.json:
            return error_response(
                status=400,
                code='INVALID_QUERY_PARAM',
                message='Category name is required'
            )

        category = Category(name=request.json['name'])

        try:
            db.session.add(category)
            db.session.commit()
        except Exception as e:
            print(e)
            return error_response(
                status=409,
                code='STATE_CONFLICT',
                message='Category already exists'
            )

        return jsonify({
            'status': 'success',
            'message': 'Category successfully created',
            'data': category.to_dict()
        }), 201
    
    ### PATCH ###
    @app.route('/categories/<int:category_id>', methods=['PATCH'])
    @jwt_required(optional=True)
    def update_category(category_id):
        """
        Update category name
        ---
        tags:
          - Categories
        security:
          - BearerAuth: []
        parameters:
          - in: path
            name: category_id
            required: true
            type: integer
          - in: body
            name: Category data
            required: true
            schema:
              type: object
              required: true
                - name
              properties:
                name:
                  type: string
                  example: "New_cat"
        responses:
          200:
            description: Category updated
          400:
            description: Invalid fields
          403:
            description: Only admins can update categories
          404:
            description: Category not found
          409:
            description: Category name already exists
        """
        claims = get_jwt()
        if claims.get("role") != "admin":
            return error_response(
                status=403,
                code='FORBIDDEN',
                message='No access'
            )

        if not request.json or 'name' not in request.json:
            return error_response(
                status=400,
                code='INVALID_QUERY_PARAM',
                message='Category name is required'
            )

        category = Category.query.get(category_id)
        if not category:
            return error_response(
                status=404,
                code='RESSOURCE_NOT_FOUND',
                message='Category ID does not exist'
            )

        try:
            category.name = request.json['name']
            db.session.commit()
        except Exception as e:
            print(e)
            return error_response(
                status=409,
                code='STATE_CONFLICT',
                message='Category name already exists'
            )

        return jsonify({
            'status': 'success',
            'message': 'Category successfully updated',
            'data': category.to_dict()
        }), 200

    ### DELETE ###
    @app.route('/categories/<int:category_id>', methods=['DELETE'])
    @jwt_required()
    def delete_category(category_id):
        """
        Delete a category
        ---
        tags:
          - Categories
        security:
          - BearerAuth: []
        parameters:
          - in: path
            name: category_id
            required: true
            type: integer
        responses:
          200:
            description: Category deleted
          403:
            description: Only admins can update categories
          404:
            description: Category not found
          409:
            description: Category has posts attached
          500:
            description: Internal servor error
        """
        claims = get_jwt()
        if claims.get("role") != "admin":
            return error_response(
                status=403,
                code='FORBIDDEN',
                message='No access'
            )

        category = Category.query.get(category_id)
        if not category:
            return error_response(
                status=404,
                code='RESSOURCE_NOT_FOUND',
                message='Category ID does not exist'
            )

        if len(category.posts) > 0:
            return error_response(
                status=409,
                code='STATE_CONFLICT',
                message='Cannot delete category with existing posts'
            )

        try:
            db.session.delete(category)
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
            'message': 'Category successfully deleted',
            'data': category.to_dict()
        }), 200

