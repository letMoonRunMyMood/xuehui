import os
import uuid

from flask import jsonify, session, request

from blueprints.course.comment import comment_bp
from blueprints.models.comment import CommentModel
from blueprints.models.course import CourseModel
from decorator import login_required
from exts import db
from tools.file_check import allowed_file



allowed_extension = {'png', 'jpg', 'jpeg'}  # 允许的图片扩展名
max_content_length= 10 * 1024 * 1024  # 限制上传大小为10MB

@comment_bp.post('/<int:course_id>/create-comment')
@login_required
def create_comment(course_id):
    try:
        if session.get('role') == 2:
            return jsonify({
                'success': False,
                'message': '管理员不可评论',
                'data': None
            }), 403
        content=request.form.get('content')
        if 'image' in request.files:
            image = request.files.get('image')
            if not allowed_file(image,allowed_extension,max_content_length) :
                return jsonify({
                    'success': False,
                    'message': '文件格式错误，支持10MB以内的png、jpg、jpeg格式图片！',
                    'data':None
                }),400
        course_id=int(course_id)
        user_id=int(request.form.get('user_id'))
        parent_id=int(request.form.get('parent_id')) # 注：楼的parent_id应为-1
        # 注：comment_type=1为楼，2为层，3为层回复
        if parent_id==-1:
            comment_type=1
        else:
            parent_comment=CommentModel.query.get(parent_id)
            if parent_comment.comment_type==1:
                comment_type=2
            else:
                comment_type=3


        course = CourseModel.query.get(course_id)
        if not course:
            return jsonify({
                'success': False,
                'message':'未找到课程！',
                'data': None
            }),404
        course_folder=course.course_folder
        folder_path=os.path.join('static/course',course_folder,'comment')
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        comment=CommentModel(
            content=content,
            course_id=course_id,
            user_id=user_id,
            parent_id=parent_id,
            comment_type=comment_type,
        )

        if 'image' in request.files:
            file_extension = os.path.splitext(image.filename)[1]
            unique_filename = f"{uuid.uuid4().hex}{file_extension}"

            saved_path = os.path.join(folder_path, unique_filename)
            image.save(saved_path)
            comment.image = saved_path

        db.session.add(comment)
        db.session.flush()
        db.session.commit()



        return jsonify({
            'success': True,
            'message':'成功创建评论',
            'data': {
                'id': comment.id,
                'content': comment.content,
                'image': comment.image,
                'course_id': course_id,
                'user_id': user_id,
                'parent_id': parent_id,
                'comment_type': comment_type,
                'created_at': comment.created_at,

            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}',
            'data': None
        }), 500