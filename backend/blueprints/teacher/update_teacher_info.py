import os
import uuid
from werkzeug.utils import secure_filename

from blueprints.models.teacher_information import TeacherInformationModel
from decorator import login_required
from exts import db
from blueprints.teacher import teacher_bp
from flask import request, jsonify, session
from blueprints.models.user import UserModel
from tools.file_check import allowed_file

allowed_extension = {'png', 'jpg', 'jpeg'}  # 允许的图片扩展名
max_content_length = 5 * 1024 * 1024  # 限制上传大小为5MB


@teacher_bp.patch('/update-teacher-info')
@login_required
def update_teacher_info():
    try:
        # 权限验证 - 只有讲师可以修改讲师信息
        if session.get('role') != 1:
            return jsonify({
                'success': False,
                'message': '用户无权限！',
                'data': None
            }), 403

        # 获取讲师对象
        teacher_id = request.form.get('teacher_id')
        if not teacher_id:
            return jsonify({
                'success': False,
                'message': '缺少讲师ID参数！',
                'data': None
            }), 400

        teacher = UserModel.query.get(teacher_id)
        teacher_information = TeacherInformationModel.query.filter_by(teacher_id=teacher_id).first()
        if not teacher:
            return jsonify({
                'success': False,
                'message': '讲师不存在！',
                'data': None
            }), 404

        # 初始化更新标志
        updated_fields = []

        # 处理表单数据（文本字段）
        if 'username' in request.form:
            teacher.username = request.form['username']
            updated_fields.append('username')

        if 'introduction' in request.form:
            teacher_information.introduction = request.form['introduction']
            updated_fields.append('introduction')

        if 'university' in request.form:
            teacher_information.university = request.form['university']
            updated_fields.append('university')

        # 处理头像图片更新
        if 'avatar' in request.files:
            avatar = request.files['avatar']

            # 验证文件
            if not allowed_file(avatar, allowed_extension, max_content_length):
                return jsonify({
                    'success': False,
                    'message': '文件格式错误，支持5MB以内的png、jpg、jpeg格式图片！',
                    'data': None
                }), 400

            # 删除旧头像（如果存在且不是默认头像）
            if teacher.avatar and not teacher.avatar.endswith('default_avatar.png'):
                old_avatar_path = teacher.avatar
                if os.path.exists(old_avatar_path):
                    try:
                        os.remove(old_avatar_path)
                    except Exception as e:
                        print(f"删除旧头像失败: {e}")
                        pass  # 删除失败不影响主要流程

            # 保存新头像
            folder_path = os.path.join('static','avatar')

            # 确保目录存在
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            # 生成唯一文件名防止覆盖
            filename = avatar.filename
            file_extension = os.path.splitext(filename)[1]
            safe_filename = f"{uuid.uuid4().hex}{file_extension.lower()}"
            saved_path = os.path.join(folder_path, safe_filename)

            avatar.save(saved_path)
            teacher.avatar = saved_path

            updated_fields.append('avatar')

        # 如果没有提供任何可更新的字段
        if not updated_fields:
            return jsonify({
                'success': False,
                'message': '未提供任何可更新的字段',
                'data': None
            }), 400

        # 提交更新
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '讲师信息更新成功',
            'data': {
                'id': teacher.id,
                'updated_fields': updated_fields,
            }
        }), 200

    except ValueError as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': '参数类型错误: ' + str(e),
            'data': None
        }), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': '服务器错误: ' + str(e),
            'data': None
        }), 500