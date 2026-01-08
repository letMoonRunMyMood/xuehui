from flask import request, jsonify, session
from decorator import login_required
from . import admin_bp
from ..models.invitation_code import InvitationCodeModel
from exts import db

@admin_bp.delete('/delete-code')
@login_required
def delete_code():
    try:
        if session.get('role') !=2:
            return jsonify({
                'success': False,
                'message': '用户无权限！',
                'data': None
            }), 403
        # 获取前端传来的邀请码ID
        code_id = request.args.get('code_id')

        # 查询要删除的邀请码
        code_to_delete = InvitationCodeModel.query.get(code_id)

        # 执行删除操作
        db.session.delete(code_to_delete)
        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '删除成功',
            'data': {'deleted_id': code_id}
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'删除失败: {str(e)}',
            'data': None
        }), 500
