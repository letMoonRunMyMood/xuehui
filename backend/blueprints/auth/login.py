from flask import request, jsonify, session
from werkzeug.security import check_password_hash
from . import auth_bp
from blueprints.models.user import UserModel


# /auth/login
@auth_bp.post('/login')
def login():
    try:
        user_data = request.form
        email = user_data.get('email')
        password = user_data.get('password')

        # 获取用户信息
        user = UserModel.query.filter_by(email=email).first()
        print('user:',user)

        if not user:
            return jsonify({
                'success': False,
                'message': "该邮箱未注册！",
                'data': None
            }), 400

        role = user.role

        if check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = role
            return jsonify({
                'success': True,
                'message': "登录成功！",
                'data':{
                    'user_id': user.id,
                    'role': role
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': "密码错误！",
                'data':None
            }), 400

    except Exception as e:
        print(e)
        return jsonify({
            "success": False,
            "message": "登录失败，请稍后再试",
            'data':None
        }), 500