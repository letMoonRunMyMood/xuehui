from flask import request, jsonify, session
from decorator import login_required
from . import admin_bp
from ..models.invitation_code import InvitationCodeModel


@admin_bp.get('/get-code')
@login_required
def get_code():
    try:
        if session.get('role') !=2:
            return jsonify({
                'success': False,
                'message': '用户无权限！',
                'data': None
            }), 403
        # 查询数据库中所有的邀请码
        codes = InvitationCodeModel.query.all()

        # 将查询结果转换为字典列表
        code_list = []
        for code in codes:
            code_list.append({
                'id': code.id,
                'email': code.email,
                'invitation_code': code.invitation_code,
                'created_at': code.created_at.strftime('%Y-%m-%d %H:%M:%S') if code.created_at else None
            })

        # 返回成功响应
        return jsonify({
            'success': True,
            'message': '成功获取邀请码列表',
            'data': code_list
        }),200

    except Exception as e:
        # 返回错误响应
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}',
            'data': None
        }), 500