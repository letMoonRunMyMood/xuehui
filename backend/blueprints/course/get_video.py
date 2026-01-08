from decorator import login_required
from . import course_bp
from flask import request, jsonify
from blueprints.models.video import VideoModel

@course_bp.get('/get-video')
@login_required
def get_video():
    try:
        video_id = int(request.args.get('video_id'))
        if not video_id:
            return jsonify({
                'success': False,
                'message': '缺少video_id参数！',
                'data': None
            }), 400

        # 查询视频基本信息
        video = VideoModel.query.get(video_id)

        if not video:
            return jsonify({
                'success': False,
                'message': '视频不存在！',
                'data': None
            }), 404

        video_url = video.file

        # 构建返回数据
        video_data = {
            'id': video.id,
            'title': video.title,
            'url': video_url,
        }

        return jsonify({
            'success': True,
            'message': '成功获取视频信息！',
            'data': video_data
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e),
            'data': None
        }), 500