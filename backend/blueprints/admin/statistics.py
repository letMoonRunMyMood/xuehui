from decorator import login_required
from exts import db
from . import admin_bp
from flask import jsonify, session
from sqlalchemy import func
from blueprints.models.course import CourseModel
from blueprints.models.grade import GradeModel
from blueprints.models.subject import SubjectModel
from blueprints.models.user import UserModel
from blueprints.models.subscribe import SubscribeModel


@admin_bp.get('/statistics')
@login_required
def get_statistics():
    """获取平台数据统计

    返回每个年级的每个科目的总订阅人数，以及每个讲师所开设的每个课程的订阅人数。
    包含详细的id和名称信息。
    """
    try:
        # 检查用户权限，只有role=2的用户才能创建广告
        if session.get('role') != 2:
            return jsonify({
                'success': False,
                'message': '用户无权限！',
                'data': None
            }), 403

        # 1. 获取每个年级的每个科目的总订阅人数
        grade_subject_stats = db.session.query(
            GradeModel.id.label('grade_id'),
            GradeModel.name.label('grade_name'),
            SubjectModel.id.label('subject_id'),
            SubjectModel.name.label('subject_name'),
            func.count(SubscribeModel.id).label('total_subscribers')
        ).join(
            CourseModel, GradeModel.id == CourseModel.grade_id
        ).join(
            SubjectModel, CourseModel.subject_id == SubjectModel.id
        ).outerjoin(
            SubscribeModel, CourseModel.id == SubscribeModel.course_id
        ).group_by(
            GradeModel.id,
            GradeModel.name,
            SubjectModel.id,
            SubjectModel.name
        ).order_by(
            GradeModel.id.asc(),
            SubjectModel.id.asc()
        ).all()

        # 2. 获取每个讲师所开设的每个课程的订阅人数
        teacher_course_stats = db.session.query(
            UserModel.id.label('teacher_id'),
            UserModel.username.label('teacher_name'),
            CourseModel.id.label('course_id'),
            CourseModel.name.label('course_name'),
            GradeModel.id.label('grade_id'),
            GradeModel.name.label('grade_name'),
            SubjectModel.id.label('subject_id'),
            SubjectModel.name.label('subject_name'),
            CourseModel.price,
            CourseModel.created_at,
            func.count(SubscribeModel.id).label('subscriber_count')
        ).join(
            CourseModel, UserModel.id == CourseModel.teacher_id
        ).join(
            GradeModel, CourseModel.grade_id == GradeModel.id
        ).join(
            SubjectModel, CourseModel.subject_id == SubjectModel.id
        ).outerjoin(
            SubscribeModel, CourseModel.id == SubscribeModel.course_id
        ).group_by(
            UserModel.id,
            UserModel.username,
            CourseModel.id,
            CourseModel.name,
            GradeModel.id,
            GradeModel.name,
            SubjectModel.id,
            SubjectModel.name,
            CourseModel.price,
            CourseModel.created_at
        ).order_by(
            UserModel.id.asc(),
            CourseModel.created_at.desc()
        ).all()

        # 3. 构建年级科目统计数据
        grade_subject_data = []
        for stat in grade_subject_stats:
            grade_subject_data.append({
                'grade_id': stat.grade_id,
                'grade_name': stat.grade_name,
                'subject_id': stat.subject_id,
                'subject_name': stat.subject_name,
                'total_subscribers': stat.total_subscribers
            })

        # 4. 构建讲师课程统计数据
        teacher_course_data = []
        for stat in teacher_course_stats:
            teacher_course_data.append({
                'teacher_id': stat.teacher_id,
                'teacher_name': stat.teacher_name,
                'course_id': stat.course_id,
                'course_name': stat.course_name,
                'grade_id': stat.grade_id,
                'grade_name': stat.grade_name,
                'subject_id': stat.subject_id,
                'subject_name': stat.subject_name,
                'price': stat.price,
                'created_at': stat.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'subscriber_count': stat.subscriber_count
            })

        # 5. 计算总体统计数据
        total_courses = len(teacher_course_data)
        total_subscribers = sum(stat.subscriber_count for stat in teacher_course_stats)
        total_teachers = len(set(stat.teacher_id for stat in teacher_course_stats))
        total_grades = len(set(stat.grade_id for stat in grade_subject_stats))
        total_subjects = len(set(stat.subject_id for stat in grade_subject_stats))

        return jsonify({
            'success': True,
            'message': '成功获取数据统计！',
            'data': {
                'grade_subject_statistics': grade_subject_data,
                'teacher_course_statistics': teacher_course_data,
                'summary': {
                    'total_courses': total_courses,
                    'total_subscribers': total_subscribers,
                    'total_teachers': total_teachers,
                    'total_grades': total_grades,
                    'total_subjects': total_subjects
                }
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取数据统计失败：{str(e)}',
            'data': None
        }), 500