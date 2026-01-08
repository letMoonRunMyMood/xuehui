import os
import uuid
from decorator import login_required
from exts import db
from . import course_bp
from flask import request, jsonify, session
from blueprints.models.course import CourseModel
from tools.file_check import allowed_file
from blueprints.models.user import UserModel
from blueprints.models.subject import SubjectModel
from blueprints.models.grade import GradeModel

allowed_extension = {'png', 'jpg', 'jpeg'}  # 允许的图片扩展名
max_content_length= 10 * 1024 * 1024  # 限制上传大小为10MB

@course_bp.post('/create-course')
@login_required
def create_course():
    try:
        if session.get('role') !=1:
            return jsonify({
                'success': False,
                'message': '用户无权限！',
                'data': None
            }), 403

        name=request.form.get('name')
        introduction=request.form.get('introduction')
        price=float(request.form.get('price'))
        teacher_id = int(request.form.get('teacher_id'))
        if UserModel.query.filter_by(id=teacher_id).first() is None:
            return jsonify({
                'success': False,
                'message': '未找到讲师！',
                'data': None
            })
        subject_id = int(request.form.get('subject_id'))
        if SubjectModel.query.filter_by(id=subject_id).first() is None:
            return jsonify({
                'success': False,
                'message': '未找到科目信息'
            })
        grade_id = int(request.form.get('grade_id'))
        if GradeModel.query.filter_by(id=grade_id).first() is None:
            return jsonify({
                'success': False,
                'message': '未找到年级信息',
                'data': None
            })
        if 'cover' in request.files:
            cover=request.files.get('cover')
            if not allowed_file(cover,allowed_extension,max_content_length) :
                return jsonify({
                    'success': False,
                    'message': '文件格式错误，支持10MB以内的png、jpg、jpeg格式图片！',
                    'data':None
                }),400

        base_folder = uuid.uuid4().hex
        folder_path = os.path.join('static/course', base_folder, 'cover')
        os.makedirs(folder_path)

        course = CourseModel(
            name=name,
            introduction=introduction,
            course_folder=base_folder,
            price=price,
            teacher_id=teacher_id,
            subject_id=subject_id,
            grade_id=grade_id,
        )
        db.session.add(course)
        db.session.commit()

        # 如果上传了封面图片
        if 'cover' in request.files:
            file_extension = os.path.splitext(cover.filename)[1]
            unique_filename = f"{uuid.uuid4().hex}{file_extension}"

            saved_path=os.path.join(folder_path,unique_filename)
            cover.save(saved_path)
            course.cover = saved_path
            db.session.commit()


        return jsonify({
            'success': True,
            'message':'成功创建课程！',
            'data':{
                'id': course.id,
                'created_at': course.created_at,
            }
        }),200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": str(e),
            "data": None
        }), 500