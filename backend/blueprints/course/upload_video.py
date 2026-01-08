import os

from decorator import login_required
from exts import db
from . import course_bp
from flask import request, jsonify, session
from blueprints.models.video import VideoModel
from blueprints.models.chapter import ChapterModel
from tools.file_check import allowed_file
import uuid

from ..models.course import CourseModel

allowed_extension = {'mp4', 'mov', 'avi', 'mkv', 'webm'}  # 允许的视频扩展名
max_content_length = 1000 * 1024 * 1024  # 限制上传大小为100MB


@course_bp.post('/upload-video')
@login_required
def upload_course():
    try:
        if session.get('role') != 1:
            return jsonify({
                'success': False,
                'message': '用户无权限！',
                'data': None
            }), 403

        chapter_id = int(request.form.get('chapter_id'))
        title = request.form.get('title')
        order = int(request.form.get('order'))

        if 'video' not in request.files:
            return jsonify({
                'success': False,
                'message': '请选择视频文件！',
                'data': None
            }), 400

        video = request.files.get('video')

        if not allowed_file(video, allowed_extension, max_content_length):
            return jsonify({
                'success': False,
                'message': '文件格式错误，支持100MB以内的mp4、avi、mov、wmv、flv、mkv格式视频！',
                'data': None
            }), 400

        # 获取章节信息及其关联的课程信息
        chapter = ChapterModel.query.get(chapter_id)
        if not chapter:
            return jsonify({
                'success': False,
                'message': '章节不存在！',
                'data': None
            }), 404

        course = CourseModel.query.get(chapter.course_id)

        # 创建视频存储目录
        video_folder_path = os.path.join('static/course', course.course_folder, 'video')
        if not os.path.exists(video_folder_path):
            os.makedirs(video_folder_path)

        # 保存视频文件
        filename = video.filename
        file_extension = os.path.splitext(filename)[1]
        safe_filename = f"{uuid.uuid4().hex}{file_extension.lower()}"
        saved_path = os.path.join(video_folder_path, safe_filename)
        video.save(saved_path)

        # 创建视频记录
        video_model = VideoModel(
            title=title,
            file=saved_path,
            order=order,
            chapter_id=chapter_id
        )
        db.session.add(video_model)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '成功上传视频！',
            'data': {
                'id': video_model.id,
                'title': video_model.title,
                'chapter_id': video_model.chapter_id,
                'order': video_model.order,
                'file_url': video_model.file  # 返回处理后的URL
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": str(e),
            "data": None
        }), 500