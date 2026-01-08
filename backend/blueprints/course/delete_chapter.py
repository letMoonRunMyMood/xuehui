import os
from decorator import login_required
from exts import db
from . import course_bp
from flask import request, jsonify, session
from blueprints.models.chapter import ChapterModel
from blueprints.models.video import VideoModel
from blueprints.models.document import DocumentModel


@course_bp.delete('/delete-chapter')
@login_required
def delete_chapter():
    try:
        # 权限验证
        if session.get('role') != 1:
            return jsonify({
                'success': False,
                'message': '用户无权限！',
                'data': None
            }), 403

        # 获取章节ID
        chapter_id = int(request.form.get('chapter_id'))
        if not chapter_id:
            return jsonify({
                'success': False,
                'message': '请提供章节ID！',
                'data': None
            }), 400

        # 查找章节记录
        chapter = ChapterModel.query.get(chapter_id)
        if not chapter:
            return jsonify({
                'success': False,
                'message': '章节不存在！',
                'data': None
            }), 404

        # 删除章节下的所有视频文件和记录
        videos = VideoModel.query.filter_by(chapter_id=chapter_id).all()
        for video in videos:
            # 删除视频物理文件
            if video.file:
                file_path = video.file
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except OSError as e:
                        return jsonify({
                            'success': False,
                            'message': f'删除视频文件失败：{str(e)}',
                            'data': None
                        }), 500
            # 删除视频记录
            db.session.delete(video)

        # 删除章节下的所有文档文件和记录
        documents = DocumentModel.query.filter_by(chapter_id=chapter_id).all()
        for document in documents:
            # 删除文档物理文件
            if document.file:
                file_path = document.file
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except OSError as e:
                        return jsonify({
                            'success': False,
                            'message': f'删除视频文件失败：{str(e)}',
                            'data': None
                        }), 500
            # 删除视频记录
            db.session.delete(document)

        # 保存章节信息用于响应
        chapter_info = {
            'id': chapter.id,
            'title': chapter.title,
            'course_id': chapter.course_id,
            'order': chapter.order,
            'deleted_videos_count': len(videos),
            'deleted_documents_count': len(documents)
        }

        # 删除章节记录
        db.session.delete(chapter)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '成功删除章节及其所有文件！',
            'data': chapter_info
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": str(e),
            "data": None
        }), 500