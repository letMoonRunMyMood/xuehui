from decorator import login_required
from exts import db
from . import course_bp
from flask import request, jsonify, session
from blueprints.models.chapter import ChapterModel
from blueprints.models.course import CourseModel


@course_bp.post('/create-chapter')
@login_required
def create_chapter():
    try:
        # 验证用户权限
        if session.get('role') != 1:
            return jsonify({
                'success': False,
                'message': '用户无权限创建章节！',
                'data': None
            }), 403

        # 获取请求数据
        title = request.form.get('title')
        course_id = int(request.form.get('course_id'))
        order = int(request.form.get('order'))

        # 验证必填字段
        if not title or not course_id:
            return jsonify({
                'success': False,
                'message': '章节标题和课程ID为必填项！',
                'data': None
            }), 400

        # 检查课程是否存在
        course = CourseModel.query.get(course_id)
        if not course:
            return jsonify({
                'success': False,
                'message': '指定的课程不存在！',
                'data': None
            }), 404

        # 创建章节
        chapter = ChapterModel(
            title=title,
            course_id=course_id,
            order=order
        )

        db.session.add(chapter)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '成功创建章节！',
            'data': {
                'id': chapter.id,
                'title': chapter.title,
                'course_id': chapter.course_id,
                'order': chapter.order
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": str(e),
            "data": None
        }), 500