from flask import request, jsonify, session

from decorator import login_required
from exts import db
from blueprints.models.user import UserModel
from blueprints.models.course import CourseModel
from blueprints.models.subscribe import SubscribeModel
from blueprints.student import student_bp

@student_bp.post('/create-subscribe')
@login_required
def create_subscription():
    try:
        # 身份验证
        if session.get('role') != 0:
            return jsonify({
                'success': False,
                'message': '用户无权限！',
                'data': None
            }), 403

        # 获取请求参数
        data = request.form

        # 参数验证
        if not data:
            return jsonify({
                'success': False,
                'message': '请求参数不能为空',
                'data': None
            }), 400

        student_id = data.get('student_id')
        course_id = data.get('course_id')

        # 必填参数检查
        if not student_id or not course_id:
            return jsonify({
                'success': False,
                'message': '学生ID和课程ID不能为空',
                'data': None
            }), 400

        # 验证学生是否存在
        student = UserModel.query.get(student_id)
        if not student:
            return jsonify({
                'success': False,
                'message': '指定的学生不存在',
                'data': None
            }), 404

        # 参数类型转换和验证
        try:
            student_id = int(student_id)
            course_id = int(course_id)
        except ValueError:
            return jsonify({
                'success': False,
                'message': '参数类型错误',
                'data': None
            }), 400

        # 验证课程是否存在
        course = CourseModel.query.get(course_id)
        if not course:
            return jsonify({
                'success': False,
                'message': '指定的课程不存在',
                'data': None
            }), 404

        # 检查订阅关系是否已存在
        existing_subscription = SubscribeModel.query.filter_by(
            student_id=student_id,
            course_id=course_id
        ).first()

        if existing_subscription:
            return jsonify({
                'success': False,
                'message': '该学生已经订阅了此课程',
                'data': {
                    'subscription_id': existing_subscription.id,
                    'student_id': student_id,
                    'course_id': course_id
                }
            }), 409

        # 创建新的订阅记录
        new_subscription = SubscribeModel(
            student_id=student_id,
            course_id=course_id
        )

        # 保存到数据库
        db.session.add(new_subscription)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '订阅成功',
            'data': {
                'subscription_id': new_subscription.id,
                'student_id': student_id,
                'course_id': course_id
            }
        }), 200

    except Exception as e:
        # 数据库回滚
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'服务器内部错误: {str(e)}',
            'data': None
        }), 500
