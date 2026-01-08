from flask import request, jsonify, session

from decorator import login_required
from exts import db
from blueprints.models.user import UserModel
from blueprints.models.course import CourseModel
from blueprints.models.favorites import FavoritesModel
from blueprints.models.subject import SubjectModel
from blueprints.models.grade import GradeModel
from blueprints.student import student_bp



@student_bp.get('/get-favorite-course')
@login_required
def get_favorite_course():
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

        # 必填参数检查
        if not student_id:
            return jsonify({
                'success': False,
                'message': '学生ID不能为空',
                'data': None
            }), 400

        # 参数类型转换和验证
        try:
            student_id = int(student_id)
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

        # 通过收藏表关联查询学生收藏的所有课程
        courses_query = db.session.query(
            CourseModel.id,
            CourseModel.name,
            CourseModel.cover,
            CourseModel.created_at,
            CourseModel.price,
            UserModel.id.label('teacher_id'),
            UserModel.username.label('teacher_username'),
            SubjectModel.id.label('subject_id'),
            SubjectModel.name.label('subject_name'),
            GradeModel.id.label('grade_id'),
            GradeModel.name.label('grade_name')
        ).join(
            FavoritesModel, CourseModel.id == FavoritesModel.course_id
        ).join(
            UserModel, CourseModel.teacher_id == UserModel.id
        ).join(
            SubjectModel, CourseModel.subject_id == SubjectModel.id
        ).join(
            GradeModel, CourseModel.grade_id == GradeModel.id
        ).filter(
            FavoritesModel.student_id == student_id
        ).order_by(
            CourseModel.created_at.desc()
        )

        courses = courses_query.all()

        # 构建返回数据
        courses_list = []
        for course in courses:
            course_info = {
                'course_id': course.id,
                'course_name': course.name,
                'course_cover': course.cover,
                'course_created_at': course.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'course_price': course.price,
                'teacher': {
                    'teacher_id': course.teacher_id,
                    'teacher_username': course.teacher_username
                },
                'subject': {
                    'subject_id': course.subject_id,
                    'subject_name': course.subject_name
                },
                'grade': {
                    'grade_id': course.grade_id,
                    'grade_name': course.grade_name
                }
            }
            courses_list.append(course_info)

        return jsonify({
            'success': True,
            'message': '获取学生收藏课程成功',
            'data': {
                'student_id': student_id,
                'total_courses': len(courses_list),
                'courses': courses_list
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'服务器内部错误: {str(e)}',
            'data': None
        }), 500