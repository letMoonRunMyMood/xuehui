import json

from flask import request, jsonify, session
import uuid
import time
from blueprints.pay import pay_bp
from decorator import login_required
from exts import logger,alipay_client


@pay_bp.post('/create_sandbox_order')
@login_required
def create_sandbox_order():
    """创建沙箱环境订单"""
    try:
        # 身份验证
        if session.get('role') != 0:
            return jsonify({
                'success': False,
                'message': '用户无权限！',
                'data': None
            }), 403

        data = request.form

        # 生成订单号（添加时间戳确保唯一性）
        order_id = f"SANDBOX_{int(time.time())}_{uuid.uuid4().hex[:8]}"

        # 订单信息
        total_amount = float(data['amount'])
        subject = data.get('subject','课程') # 商品名
        student_id=int(data.get('student_id'))
        course_id=int(data.get('course_id'))
        base_url=data.get('base_url') # 返回的地址

        body={'student_id':student_id,'course_id':course_id,'base_url':base_url}


        # 创建沙箱支付订单
        pay_url = alipay_client.create_sandbox_web_pay(
            order_id=order_id,
            amount=total_amount,
            subject=subject,
            body=json.dumps(body),
            return_url=base_url
        )

        if pay_url:
            logger.info(f"沙箱订单创建成功: {order_id}")
            return jsonify({
                'success': True,
                'order_id': order_id,
                'pay_url': pay_url, # 订单支付页面
                'environment': 'sandbox'
            }),200
        else:
            del alipay_client.orders[order_id]
            return jsonify({
                'success': False,
                'message': '创建沙箱支付订单失败'
            }), 400

    except Exception as e:
        logger.error(f"创建沙箱订单异常: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'创建订单失败: {str(e)}'
        }), 500