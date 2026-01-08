from flask import jsonify, session, request
from decorator import login_required
from blueprints.models.user import UserModel
from blueprints.models.video import VideoModel
from blueprints.models.play_progress import PlayProgressModel
from . import course_bp

@course_bp.get('/get-progress')
@login_required
def get_progress():
    try:
        # 获取请求参数
        user_id = request.args.get('user_id')
        video_id = request.args.get('video_id')

        # 必填参数检查
        if not user_id or not video_id:
            return jsonify({
                'success': False,
                'message': '用户ID和视频ID不能为空',
                'data': None
            }), 400

        # 参数类型转换和验证
        try:
            user_id = int(user_id)
            video_id = int(video_id)
        except ValueError:
            return jsonify({
                'success': False,
                'message': '参数类型错误',
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

        # 查询播放进度记录
        progress_record = PlayProgressModel.query.filter_by(
            user_id=user_id,
            video_id=video_id
        ).first()

        if progress_record:
            # 返回播放进度信息
            return jsonify({
                'success': True,
                'message': '获取播放进度成功',
                'data': {
                    'have_progress':True,
                    'progress_id': progress_record.id,
                    'user_id': user_id,
                    'video_id': video_id,
                    'progress': progress_record.progress,
                    'last_updated': progress_record.last_updated.strftime('%Y-%m-%d %H:%M:%S')
                }
            }), 200
        else:
            # 没有播放进度记录，返回默认进度0
            return jsonify({
                'success': True,
                'message': '未找到播放进度记录，返回默认进度',
                'data': {
                    'have_progress': False,
                    'progress_id': None,
                    'user_id': user_id,
                    'video_id': video_id,
                    'progress': 0.0,
                    'last_updated': None
                }
            }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'服务器内部错误: {str(e)}',
            'data': None
        }), 500