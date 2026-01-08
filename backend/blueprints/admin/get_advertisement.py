from decorator import login_required
from . import admin_bp
from flask import jsonify
from blueprints.models.advertisement import AdvertisementModel

@admin_bp.get('/get-advertisement')
@login_required
def get_advertisement():
    try:
        # 查询所有广告
        advertisements = AdvertisementModel.query.all()

        if not advertisements:
            return jsonify({
                'success': True,
                'message': '暂无广告数据！',
                'data': []
            }), 200

        # 构建返回数据
        advertisements_data = []
        for advertisement in advertisements:
            image_url = advertisement.image

            advertisement_data = {
                'id': advertisement.id,
                'name': advertisement.name,
                'link': advertisement.link,
                'image': image_url,
            }
            advertisements_data.append(advertisement_data)

        return jsonify({
            'success': True,
            'message': '成功获取广告信息！',
            'data': advertisements_data
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e),
            'data': None
        }), 500