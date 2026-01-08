from flask import request, jsonify, session

from decorator import login_required
from exts import db
from blueprints.models.subscribe import SubscribeModel
from blueprints.student import student_bp

@student_bp.delete('/cancel-subscribe')
@login_required
def cancel_subscribe():
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

        # 查找订阅记录
        subscription = SubscribeModel.query.filter_by(
            student_id=student_id,
            course_id=course_id
        ).first()

        if not subscription:
            return jsonify({
                'success': False,
                'message': '订阅关系不存在',
                'data': None
            }), 404

        # 删除订阅记录
        db.session.delete(subscription)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '取消订阅成功',
            'data': {
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
