import os

from decorator import login_required
from exts import db
from . import course_bp
from flask import request, jsonify, session
from blueprints.models.video import VideoModel


@course_bp.delete('/delete-video')
@login_required
def delete_video():
    try:
        # 权限验证
        if session.get('role') != 1:
            return jsonify({
                'success': False,
                'message': '用户无权限！',
                'data': None
            }), 403

        # 获取视频ID
        video_id = int(request.form.get('video_id'))
        if not video_id:
            return jsonify({
                'success': False,
                'message': '请提供视频ID！',
                'data': None
            }), 400

        # 查找视频记录
        video = VideoModel.query.get(video_id)
        if not video:
            return jsonify({
                'success': False,
                'message': '视频不存在！',
                'data': None
            }), 404

        # 删除物理文件
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

        # 保存视频信息用于响应
        video_info = {
            'id': video.id,
            'title': video.title,
            'chapter_id': video.chapter_id,
            'order': video.order
        }

        # 删除数据库记录
        db.session.delete(video)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '成功删除视频！',
            'data': video_info
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": str(e),
            "data": None
        }), 500