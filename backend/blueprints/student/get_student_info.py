
from flask import jsonify, session, request

from blueprints.models.student_information import StudentInformationModel
from blueprints.models.user import UserModel
from blueprints.student import student_bp
from decorator import login_required


@student_bp.get('/get-student-info')
@login_required
def get_student_info():
    try:
        # 身份验证
        if session.get('role') != 0:
            return jsonify({
                'success': False,
                'message': '用户无权限！',
                'data': None
            }), 403
        # 获取学生ID参数
        student_id = int(request.args.get('student_id'))

        # 参数验证
        if not student_id:
            return jsonify({
                'success': False,
                'message': '缺少学生ID参数！',
                'data': None
            }), 400

        student = UserModel.query.get(student_id)
        if not student:
            return jsonify({
                'success': False,
                'message':'未找到学生数据！',
                'data': None
            }),404

        student_information=StudentInformationModel.query.filter_by(student_id=student_id).first()
        if not student_information:
            return jsonify({
                'success': False,
                'message': '学生信息不存在！',
                'data': None
            }), 404

        avatar=student.avatar

        return jsonify({
            'success': True,
            'message':'成功获取学生数据！',
            'data': {
                'avatar': avatar,
                'email': student.email,
                'username': student.username,
                'join_time': student.join_time,
                'grade': student_information.grade,
            }
        }),200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e),
            'data': None
        }), 500
