from flask import jsonify
from services.user_service import get_all_users
from error_response import error_response

def register_user_routes(app):

    @app.route("/users", methods=["GET"])
    def get_users():
        try:
            users = get_all_users()
            return jsonify({
                "status": "success",
                "data": users
            }), 200
        except Exception:
            return error_response(500, "INTERNAL_SERVER_ERROR", "Internal server error")
