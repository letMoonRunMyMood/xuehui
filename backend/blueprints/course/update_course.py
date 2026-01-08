import os
import uuid
from werkzeug.utils import secure_filename

from decorator import login_required
from exts import db
from . import course_bp
from flask import request, jsonify, session
from blueprints.models.course import CourseModel
from tools.file_check import allowed_file


allowed_extension = {'png', 'jpg', 'jpeg'}  # 允许的图片扩展名
max_content_length= 5 * 1024 * 1024  # 限制上传大小为5MB


@course_bp.patch('/update-course')
@login_required
def update_course():
    try:
        # 权限验证 - 只有讲师可以修改课程
        if session.get('role') != 1:
            return jsonify({
                'success': False,
                'message': '用户无权限！',
                'data': None
            }), 403

        # 获取课程对象
        course_id = request.form.get('course_id')
        course = CourseModel.query.get(course_id)
        if not course:
            return jsonify({
                'success': False,
                'message': '课程不存在！',
                'data': None
            }), 404

        # 初始化更新标志
        updated_fields = []

        # 处理表单数据（文本字段）
        if 'name' in request.form and request.form['name'] != course.name:
            old_name = course.name
            course.name = request.form['name']
            updated_fields.append('name')

        if 'introduction' in request.form:
            course.introduction = request.form['introduction']
            updated_fields.append('introduction')

        if 'price' in request.form:
            course.price = float(request.form['price'])
            updated_fields.append('price')

        if 'subject_id' in request.form:
            course.subject_id = int(request.form['subject_id'])
            updated_fields.append('subject_id')

        if 'grade_id' in request.form:
            course.grade_id = int(request.form['grade_id'])
            updated_fields.append('grade_id')

        # 处理封面图片更新
        if 'cover' in request.files:
            cover = request.files['cover']

            # 验证文件
            if not allowed_file(cover, allowed_extension, max_content_length):
                return jsonify({
                    'success': False,
                    'message': '文件格式错误，支持5MB以内的png、jpg、jpeg格式图片！',
                    'data': None
                }), 400

            # 删除旧封面（如果存在）
            if course.cover:
                # 获取实际文件路径（移除/static/前缀并转换路径）
                old_cover_path = str(course.cover)
                if os.path.exists(old_cover_path) and old_cover_path != '/static/default/default_cover.jpg':
                    try:
                        os.remove(old_cover_path)
                    except Exception as e:
                        print(f"删除旧封面失败: {e}")
                        pass  # 删除失败不影响主要流程

            # 保存新封面
            base_folder = course.course_folder
            folder_path = os.path.join('static/course', base_folder, 'cover')

            # 确保目录存在
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            # 获取文件扩展名并生成唯一文件名
            file_extension = os.path.splitext(cover.filename)[1]
            unique_filename = f"{uuid.uuid4().hex}{file_extension}"
            saved_path = os.path.join(folder_path, unique_filename)

            cover.save(saved_path)
            course.cover = saved_path

            updated_fields.append('cover')

        # 如果没有提供任何可更新的字段
        if not updated_fields:
            return jsonify({
                'success': False,
                'message': '未提供任何可更新的字段',
                'data': None
            }), 400

        # 更新修改时间
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '课程信息更新成功',
            'data': {
                'id': course.id,
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