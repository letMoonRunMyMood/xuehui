
from flask import jsonify, session, request

from blueprints.models.teacher_information import TeacherInformationModel
from blueprints.models.user import UserModel
from blueprints.teacher import teacher_bp
from decorator import login_required


@teacher_bp.get('get-teacher-info')
@login_required
def get_teacher_info():
    try:
        # 身份验证
        if session.get('role') != 1:
            return jsonify({
                'success': False,
                'message': '用户无权限！',
                'data': None
            }), 403
        # 获取讲师ID参数
        teacher_id = int(request.args.get('teacher_id'))

        # 参数验证
        if not teacher_id:
            return jsonify({
                'success': False,
                'message': '缺少讲师ID参数！',
                'data': None
            }), 400

        teacher = UserModel.query.get(teacher_id)
        if not teacher:
            return jsonify({
                'success': False,
                'message':'未找到讲师数据！',
                'data': None
            }),404

        teacher_information = TeacherInformationModel.query.filter_by(teacher_id=teacher_id).first()
        if not teacher_information:
            return jsonify({
                'success': False,
                'message':'未找到讲师详细信息！',
                'data': None
            }),404

        avatar=teacher.avatar

        return jsonify({
            'success': True,
            'message':'成功获取讲师数据！',
            'data': {
                'avatar': avatar,
                'email': teacher.email,
                'username': teacher.username,
                'join_time': teacher.join_time,
                'university': teacher_information.university,
                'introduction': teacher_information.introduction,
            }
        }),200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e),
            'data': None
        }), 500