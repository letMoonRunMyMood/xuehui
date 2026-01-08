import os
import uuid
from decorator import login_required
from exts import db
from . import admin_bp
from flask import request, jsonify, session
from blueprints.models.advertisement import AdvertisementModel
from tools.file_check import allowed_file

allowed_extension = {'png', 'jpg', 'jpeg'}  # 允许的图片扩展名
max_content_length = 30 * 1024 * 1024  # 限制上传大小为5MB


@admin_bp.post('/create-advertisement')
@login_required
def create_advertisement():
    try:
        # 检查用户权限，只有role=2的用户才能创建广告
        if session.get('role') != 2:
            return jsonify({
                'success': False,
                'message': '用户无权限！',
                'data': None
            }), 403

        # 获取表单数据
        name = request.form.get('name')
        link = request.form.get('link')

        # 验证必填字段
        if not name or not link:
            return jsonify({
                'success': False,
                'message': '广告名称和链接不能为空！',
                'data': None
            }), 400

        # 验证图片文件
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'message': '请上传广告图片！',
                'data': None
            }), 400

        image = request.files.get('image')
        if not allowed_file(image, allowed_extension, max_content_length):
            return jsonify({
                'success': False,
                'message': '文件格式错误，支持30MB以内的png、jpg、jpeg格式图片！',
                'data': None
            }), 400

        # 创建文件夹并保存图片
        folder_path = os.path.join('static', 'advertisement')
        os.makedirs(folder_path, exist_ok=True)
        filename = image.filename
        file_extension = os.path.splitext(filename)[1]
        safe_filename = f"{uuid.uuid4().hex}{file_extension.lower()}"
        saved_path = os.path.join(folder_path, safe_filename)
        image.save(saved_path)

        advertisement = AdvertisementModel(
            name=name,
            link=link,
            image=saved_path
        )
        db.session.add(advertisement)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '成功创建广告！',
            'data': {
                'id': advertisement.id,
                'name': advertisement.name,
                'link': advertisement.link,
                'image': advertisement.image
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": str(e),
            "data": None
        }), 500