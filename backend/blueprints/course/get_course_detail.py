from decorator import login_required
from exts import db
from . import course_bp
from flask import request, jsonify
from blueprints.models.course import CourseModel
from blueprints.models.grade import GradeModel
from blueprints.models.subject import SubjectModel
from blueprints.models.user import UserModel
from blueprints.models.chapter import ChapterModel
from blueprints.models.video import VideoModel
from blueprints.models.document import DocumentModel
from blueprints.models.teacher_information import TeacherInformationModel


@course_bp.get('/get-course-detail')
@login_required
def get_course_detail():
    try:
        course_id = int(request.args.get('course_id'))
        if not course_id:
            return jsonify({
                'success': False,
                'message': '缺少course_id参数！',
                'data': None
            }), 400

        # 查询课程基本信息及关联信息
        course = db.session.query(
            CourseModel.id,
            CourseModel.name,
            CourseModel.cover,
            CourseModel.introduction,
            CourseModel.created_at,
            CourseModel.price,
            CourseModel.grade_id,
            GradeModel.name.label('grade_name'),
            CourseModel.subject_id,
            SubjectModel.name.label('subject_name'),
            CourseModel.teacher_id,
            UserModel.username,
            UserModel.avatar,
            TeacherInformationModel.introduction.label('teacher_introduction'),
            TeacherInformationModel.university
        ).join(
            GradeModel, CourseModel.grade_id == GradeModel.id
        ).join(
            SubjectModel, CourseModel.subject_id == SubjectModel.id
        ).join(
            UserModel, CourseModel.teacher_id == UserModel.id
        ).join(
            TeacherInformationModel, UserModel.id == TeacherInformationModel.teacher_id
        ).filter(CourseModel.id == course_id).first()

        if not course:
            return jsonify({
                'success': False,
                'message': '课程不存在！',
                'data': None
            }), 404

        # 图片路径
        cover_url = course.cover
        avatar_url = course.avatar

        # 查询课程章节信息
        chapters = db.session.query(ChapterModel).filter(
            ChapterModel.course_id == course_id
        ).order_by(ChapterModel.order).all()

        chapters_data = []
        for chapter in chapters:
            # 查询章节视频
            videos = db.session.query(VideoModel).filter(
                VideoModel.chapter_id == chapter.id
            ).order_by(VideoModel.order).all()

            videos_data = []
            for video in videos:
                videos_data.append({
                    'id': video.id,
                    'title': video.title,
                    'order': video.order
                })

            # 查询章节文档
            documents = db.session.query(DocumentModel).filter(
                DocumentModel.chapter_id == chapter.id
            ).all()

            documents_data = []
            for document in documents:
                documents_data.append({
                    'id': document.id,
                    'title': document.title
                })

            chapters_data.append({
                'id': chapter.id,
                'title': chapter.title,
                'order': chapter.order,
                'videos': videos_data,
                'documents': documents_data
            })

        # 构建返回数据
        course_data = {
            'id': course.id,
            'name': course.name,
            'cover': cover_url,
            'introduction': course.introduction,
            'created_at': course.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'price': course.price,
            'grade_id': course.grade_id,
            'grade_name': course.grade_name,
            'subject_id': course.subject_id,
            'subject_name': course.subject_name,
            'teacher_id': course.teacher_id,
            'teacher': {
                'username': course.username,
                'avatar': avatar_url,
                'introduction': course.teacher_introduction,
                'university': course.university
            },
            'chapters': chapters_data
        }

        return jsonify({
            'success': True,
            'message': '成功获取课程详情！',
            'data': course_data
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e),
            'data': None
        }), 500