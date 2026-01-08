from flask import jsonify, session, request

from decorator import login_required
from exts import db
from blueprints.models.user import UserModel
from blueprints.models.video import VideoModel
from blueprints.models.play_progress import PlayProgressModel
from datetime import datetime

from . import course_bp


@course_bp.post('/save-progress')
@login_required
def save_progress():
    try:
        # 获取请求参数
        data = request.form

        # 参数验证
        if not data:
            return jsonify({
                'success': False,
                'message': '请求参数不能为空',
                'data': None
            }), 400

        user_id = data.get('user_id')
        video_id = data.get('video_id')
        progress = data.get('progress')

        # 必填参数检查
        if not user_id or not video_id or progress is None:
            return jsonify({
                'success': False,
                'message': '用户ID、视频ID和播放进度不能为空',
                'data': None
            }), 400

        # 参数类型转换和验证
        try:
            user_id = int(user_id)
            video_id = int(video_id)
            progress = float(progress)
        except ValueError:
            return jsonify({
                'success': False,
                'message': '参数类型错误',
                'data': None
            }), 400

        # 验证播放进度范围
        if progress < 0.0 or progress > 1.0:
            return jsonify({
                'success': False,
                'message': '播放进度必须在0到1之间',
                'data': None
            }), 400

        # 验证用户是否存在
        user = UserModel.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': '指定的用户不存在',
                'data': None
            }), 404

        # 验证视频是否存在
        video = VideoModel.query.get(video_id)
        if not video:
            return jsonify({
                'success': False,
                'message': '指定的视频不存在',
                'data': None
            }), 404

        # 检查播放进度记录是否已存在
        existing_progress = PlayProgressModel.query.filter_by(
            user_id=user_id,
            video_id=video_id
        ).first()

        if existing_progress:
            # 更新现有记录
            existing_progress.progress = progress
            existing_progress.last_updated = datetime.now()

            db.session.commit()

            return jsonify({
                'success': True,
                'message': '播放进度更新成功',
                'data': {
                    'progress_id': existing_progress.id,
                    'user_id': user_id,
                    'video_id': video_id,
                    'progress': progress,
                    'last_updated': existing_progress.last_updated.strftime('%Y-%m-%d %H:%M:%S')
                }
            }), 200
        else:
            # 创建新的播放进度记录
            new_progress = PlayProgressModel(
                user_id=user_id,
                video_id=video_id,
                progress=progress
            )
            # 保存到数据库
            db.session.add(new_progress)
            db.session.commit()
            return jsonify({
                'success': True,
                'message': '播放进度保存成功',
                'data': {
                    'progress_id': new_progress.id,
                    'user_id': user_id,
                    'video_id': video_id,
                    'progress': progress,
                    'last_updated': new_progress.last_updated.strftime('%Y-%m-%d %H:%M:%S')
                }
            }), 200

    except Exception as e:
        # 数据库回滚
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'服务器内部错误: {str(e)}',
            'data': None
        }), 500