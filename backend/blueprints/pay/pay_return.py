import json

from flask import request, jsonify, redirect
from blueprints.pay import pay_bp
from exts import logger, alipay_client


@pay_bp.get('/pay_return')
def pay_return():
    try:
        # 获取请求参数中的订单ID
        data = request.args.to_dict()
        if alipay_client.verify_sandbox_notify(data.copy()):
            base_url = json.loads(data.get('body'))['base_url']
            print
            return redirect(base_url)

    except Exception as e:
        logger.error(f"支付返回处跳转异常: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'处理失败: {str(e)}'
        }), 500
