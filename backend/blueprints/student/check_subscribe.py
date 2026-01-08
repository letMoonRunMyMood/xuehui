from flask import request, jsonify, session
from blueprints.models.user import UserModel
from blueprints.models.course import CourseModel
from blueprints.models.subscribe import SubscribeModel
from blueprints.student import student_bp
from decorator import login_required


@student_bp.get('/check-subscribe')
@login_required
def check_subscription():
    try:
        # 身份验证
        if session.get('role') != 0:
            return jsonify({
                'success': False,
                'message': '用户无权限！',
                'data': None
            }), 403

        # 获取请求参数
        data = request.args.to_dict()

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

        # 验证学生是否存在
        student = UserModel.query.get(student_id)
        if not student:
            return jsonify({
                'success': False,
                'message': '指定的学生不存在',
                'data': None
            }), 404

        # 验证课程是否存在
        course = CourseModel.query.get(course_id)
        if not course:
            return jsonify({
                'success': False,
                'message': '指定的课程不存在',
                'data': None
            }), 404

        # 检查订阅关系是否存在
        subscription = SubscribeModel.query.filter_by(
            student_id=student_id,
            course_id=course_id
        ).first()

        if subscription:
            return jsonify({
                'success': True,
                'message': '学生已订阅此课程',
                'data': {
                    'is_subscribed': True,
                    'subscription_id': subscription.id,
                    'student_id': student_id,
                    'course_id': course_id,
                    'student_name': student.username,
                    'course_name': course.name
                }
            }), 200
        else:
            return jsonify({
                'success': True,
                'message': '学生未订阅此课程',
                'data': {
                    'is_subscribed': False,
                    'student_id': student_id,
                    'course_id': course_id,
                    'student_name': student.username,
                    'course_name': course.name
                }
            }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'服务器内部错误: {str(e)}',
            'data': None
        }), 500