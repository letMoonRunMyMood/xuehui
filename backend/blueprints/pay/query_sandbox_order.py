from flask import jsonify
from blueprints.pay import pay_bp
from exts import logger,alipay_client

@pay_bp.get('/query_sandbox_order/<order_id>')
def query_sandbox_order(order_id):
    """查询沙箱环境订单状态"""
    try:
        alipay_result = alipay_client.query_sandbox_order(order_id)
        if alipay_result:
            return jsonify({
                'success': True,
                'alipay_result': alipay_result,
                'environment': 'sandbox',
            }),200
        else:
            return jsonify({
                'success': False,
                'message': '订单不存在！'
            }), 404

    except Exception as e:
        logger.error(f"查询沙箱订单异常: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'查询失败: {str(e)}'
        }), 500