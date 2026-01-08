import os

from decorator import login_required
from exts import db
from . import admin_bp
from flask import request, jsonify, session
from blueprints.models.advertisement import AdvertisementModel


@admin_bp.delete('/delete-advertisement')
@login_required
def delete_advertisement():
    try:
        # 权限验证，只有role=2的用户才能删除广告
        if session.get('role') != 2:
            return jsonify({
                'success': False,
                'message': '用户无权限！',
                'data': None
            }), 403

        # 获取广告ID
        advertisement_id = int(request.form.get('advertisement_id'))
        if not advertisement_id:
            return jsonify({
                'success': False,
                'message': '请提供广告ID！',
                'data': None
            }), 400

        # 查找广告记录
        advertisement = AdvertisementModel.query.get(advertisement_id)
        if not advertisement:
            return jsonify({
                'success': False,
                'message': '广告不存在！',
                'data': None
            }), 404

        # 删除物理文件
        if advertisement.image:
            file_path = advertisement.image

            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError as e:
                    return jsonify({
                        'success': False,
                        'message': f'删除广告图片失败：{str(e)}',
                        'data': None
                    }), 500

        # 保存广告信息用于响应
        advertisement_info = {
            'id': advertisement.id,
            'name': advertisement.name,
            'link': advertisement.link,
            'image': advertisement.image
        }

        # 删除数据库记录
        db.session.delete(advertisement)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '成功删除广告！',
            'data': advertisement_info
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": str(e),
            "data": None
        }), 500