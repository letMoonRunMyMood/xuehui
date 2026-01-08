import os

from decorator import login_required
from exts import db
from . import course_bp
from flask import request, jsonify, session
from blueprints.models.document import DocumentModel


@course_bp.delete('/delete-document')
@login_required
def delete_document():
    try:
        # 权限验证
        if session.get('role') != 1:
            return jsonify({
                'success': False,
                'message': '用户无权限！',
                'data': None
            }), 403

        # 获取文档ID
        document_id = request.form.get('document_id')
        if not document_id:
            return jsonify({
                'success': False,
                'message': '请提供文档ID！',
                'data': None
            }), 400

        # 类型转换
        try:
            document_id = int(document_id)
        except ValueError:
            return jsonify({
                'success': False,
                'message': '文档ID格式错误！',
                'data': None
            }), 400

        # 查找文档记录
        document = DocumentModel.query.get(document_id)
        if not document:
            return jsonify({
                'success': False,
                'message': '文档不存在！',
                'data': None
            }), 404

        # 删除物理文件
        if document.file:
            file_path = document.file

            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError as e:
                    return jsonify({
                        'success': False,
                        'message': f'删除视频文件失败：{str(e)}',
                        'data': None
                    }), 500

        # 保存文档信息用于响应
        document_info = {
            'id': document.id,
            'title': document.title,
            'chapter_id': document.chapter_id
        }

        # 删除数据库记录
        db.session.delete(document)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '成功删除文档！',
            'data': document_info
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": str(e),
            "data": None
        }), 500