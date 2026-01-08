from flask import request, jsonify
import requests
import json
from blueprints.models.course import CourseModel
from blueprints.models.subscribe import SubscribeModel
from blueprints.pay import pay_bp
from exts import logger, alipay_client, db
from blueprints.models.payment_record import PaymentRecordModel


@pay_bp.post('/pay_notify')
def pay_notify():
    try:
        # 获取请求参数中的订单信息
        data = request.form.to_dict()
        print('notify:',data)
        if alipay_client.verify_sandbox_notify(data.copy()):
            order_id = data.get('out_trade_no')
            body=json.loads(data.get('body'))
            student_id = body['student_id']
            course_id = body['course_id']
            course = CourseModel.query.get(course_id)
            if not order_id:
                return jsonify({
                    'success': False,
                    'message': '缺少订单ID参数'
                }), 400

            # 向查询接口发起请求
            response = requests.get(f'http://localhost:5000/pay/query_sandbox_order/{order_id}')
            payment_record=PaymentRecordModel(
                id=order_id,
                course_id=course_id,
                course_name=course.name,
                student_id=student_id,
                amount=float(response.json().get('alipay_result').get('total_amount')),
            )
            subscribe=SubscribeModel(
                student_id=student_id,
                course_id=course_id,
            )
            # 打印返回数据
            print("查询接口返回数据:", response.json())
            try:
                alipay_client.orders.pop(order_id)
            except Exception as e:
                print(e)

            db.session.add(payment_record)
            db.session.add(subscribe)
            db.session.commit()
            # 返回原始数据
            return jsonify({
                'success': True,
                'message': '支付处理成功！',
            }), 200

    except Exception as e:
        logger.error(f"支付返回处理异常: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'处理失败: {str(e)}'
        }), 500