from flask import session, g, jsonify
from blueprints.models.user import UserModel

def login_before_request(app):
    @app.before_request
    def my_before_request():
        try:
            user_id = session.get("user_id")
            role = session.get("role")
            print("before request", role,user_id)
            user = UserModel.query.get(user_id)
            setattr(g, "user", user)
        except Exception as e:
            return jsonify({
                "success": False,
                "message": str(e)
            }), 500
