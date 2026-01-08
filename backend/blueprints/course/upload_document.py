import os

from decorator import login_required
from exts import db
from . import course_bp
from flask import request, jsonify, session
from blueprints.models.document import DocumentModel
from blueprints.models.chapter import ChapterModel
from tools.file_check import allowed_file
import uuid

from ..models.course import CourseModel

allowed_extension = {'pdf', 'doc', 'docx', 'ppt', 'pptx'}  # 允许的文档扩展名
max_content_length = 50 * 1024 * 1024  # 限制上传大小为50MB


@course_bp.post('/upload-document')
@login_required
def upload_document():
    try:
        if session.get('role') != 1:
            return jsonify({
                'success': False,
                'message': '用户无权限！',
                'data': None
            }), 403

        chapter_id = int(request.form.get('chapter_id'))
        title = request.form.get('title')

        if 'document' not in request.files:
            return jsonify({
                'success': False,
                'message': '请选择文档文件！',
                'data': None
            }), 400

        document = request.files.get('document')

        if not allowed_file(document, allowed_extension, max_content_length):
            return jsonify({
                'success': False,
                'message': '文件格式错误，支持50MB以内的pdf、doc、docx、ppt、pptx格式文档！',
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

        # 创建文档存储目录
        document_folder_path = os.path.join('static/course', course.course_folder, 'document')
        if not os.path.exists(document_folder_path):
            os.makedirs(document_folder_path)

        # 保存文档文件
        filename = document.filename
        file_extension = os.path.splitext(filename)[1]
        safe_filename = f"{uuid.uuid4().hex}{file_extension.lower()}"
        saved_path = os.path.join(document_folder_path, safe_filename)
        document.save(saved_path)

        # 创建文档记录
        document_model = DocumentModel(
            title=title,
            file=saved_path,
            chapter_id=chapter_id
        )
        db.session.add(document_model)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '成功上传文档！',
            'data': {
                'id': document_model.id,
                'title': document_model.title,
                'chapter_id': document_model.chapter_id,
                'file_url': document_model.file  # 返回处理后的URL
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": str(e),
            "data": None
        }), 500