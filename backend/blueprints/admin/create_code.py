from flask import request, jsonify, session
from exts import db
from . import admin_bp
import random
import string
from ..models.invitation_code import InvitationCodeModel
from decorator import login_required


@admin_bp.post("/create-code")
@login_required
def create_code():
    try:
        if session.get('role') !=2:
            return jsonify({
                'success': False,
                'message': '用户无权限！',
                'data': None
            }), 403
        email = request.form.get("email")
        invitation_code = generate_random_string(10)
        invitation_code_model = InvitationCodeModel(email=email, invitation_code=invitation_code)
        db.session.add(invitation_code_model)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "成功生成邀请码",
            "data": {
                "id": invitation_code_model.id,
                "email": email,
                "invitation_code": invitation_code,
                "created_at": invitation_code_model.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

def generate_random_string(length=10):
    """
    生成指定长度的随机字符串（包含大小写字母和数字）

    参数:
        length (int): 字符串长度，默认为10

    返回:
        str: 随机生成的字符串
    """
    # 定义字符集：大小写字母+数字
    characters = string.ascii_letters + string.digits
    # 从字符集中随机选择指定长度的字符
    return ''.join(random.choices(characters, k=length))