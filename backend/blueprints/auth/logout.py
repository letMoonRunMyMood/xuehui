from flask import session, jsonify
from . import auth_bp

'''
本接口进行了请求方法修改
'''

# /auth/logout
@auth_bp.post('/logout')
def logout():
    try:
        session.clear()
        return jsonify({
            "success": True,
            "message": "已退出登录！"
        }),200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500