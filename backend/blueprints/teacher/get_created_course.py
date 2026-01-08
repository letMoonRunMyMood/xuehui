from sqlalchemy import func

from decorator import login_required
from exts import db
from . import teacher_bp
from flask import request, jsonify, session
from blueprints.models.course import CourseModel
from ..models.subscribe import SubscribeModel


@teacher_bp.get('/get-created-course')
@login_required
def get_created_course():
    try:
        # 身份验证
        if session.get('role') != 1:
            return jsonify({
                'success': False,
                'message': '用户无权限！',
                'data': None
            }), 403

        # 获取讲师ID参数
        teacher_id = request.args.get('teacher_id')

        # 参数验证
        if not teacher_id:
            return jsonify({
                'success': False,
                'message': '缺少讲师ID参数！',
                'data': None
            }), 400

        try:
            teacher_id = int(teacher_id)
        except ValueError:
            return jsonify({
                'success': False,
                'message': '讲师ID参数格式错误！',
                'data': None
            }), 400

        # 查询该讲师创建的所有课程，并统计订阅人数
        courses = db.session.query(
            CourseModel.id,
            CourseModel.name,
            CourseModel.cover,
            CourseModel.created_at,
            func.count(SubscribeModel.id).label('subscriber_count')
        ).outerjoin(
            SubscribeModel, CourseModel.id == SubscribeModel.course_id
        ).filter(
            CourseModel.teacher_id == teacher_id
        ).group_by(
            CourseModel.id
        ).order_by(CourseModel.created_at.desc()).all()

        # 构建返回数据
        courses_data = []
        for course in courses:
            cover_url = course.cover
            if cover_url:
                cover_url = cover_url

            courses_data.append({
                'id': course.id,
                'name': course.name,
                'cover': cover_url,
                'created_at': course.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'subscriber_count': course.subscriber_count
            })

        return jsonify({
            'success': True,
            'message': '成功获取讲师创建的课程列表！',
            'data': {
                'courses': courses_data,
                'total': len(courses_data),
                'teacher_id': teacher_id
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e),
            'data': None
        }), 500