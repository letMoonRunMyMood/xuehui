from decorator import login_required
from exts import db
from . import course_bp
from flask import jsonify
from sqlalchemy import func
from blueprints.models.course import CourseModel
from blueprints.models.grade import GradeModel
from blueprints.models.subject import SubjectModel
from blueprints.models.user import UserModel
from blueprints.models.subscribe import SubscribeModel


@course_bp.get('/get-courses')
@login_required
def get_courses():
    try:
        # 查询获取课程及其关联信息，并统计订阅人数
        courses = db.session.query(
            CourseModel.id,
            CourseModel.name,
            CourseModel.cover,
            CourseModel.created_at,
            CourseModel.price,
            CourseModel.grade_id,
            GradeModel.name.label('grade_name'),
            CourseModel.subject_id,
            SubjectModel.name.label('subject_name'),
            CourseModel.teacher_id,
            UserModel.username.label('teacher_name'),
            func.count(SubscribeModel.id).label('subscriber_count')
        ).join(
            GradeModel, CourseModel.grade_id == GradeModel.id
        ).join(
            SubjectModel, CourseModel.subject_id == SubjectModel.id
        ).join(
            UserModel, CourseModel.teacher_id == UserModel.id
        ).outerjoin(
            SubscribeModel, CourseModel.id == SubscribeModel.course_id
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
                'price': course.price,
                'grade_id': course.grade_id,
                'grade_name': course.grade_name,
                'subject_id': course.subject_id,
                'subject_name': course.subject_name,
                'teacher_id': course.teacher_id,
                'teacher_name': course.teacher_name,
                'subscriber_count': course.subscriber_count
            })

        return jsonify({
            'success': True,
            'message': '成功获取课程列表！',
            'data': {
                'courses': courses_data,
                'total': len(courses_data)
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e),
            'data': None
        }), 500