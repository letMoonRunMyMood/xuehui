from flask import Blueprint, request, jsonify, session

from decorator import login_required
from exts import db
from blueprints.models.user import UserModel
from blueprints.models.payment_record import PaymentRecordModel
from blueprints.student import student_bp


@student_bp.get('/get-payment-records')
@login_required
def get_payment_records():
    try:
        # 身份验证
        if session.get('role') != 0:
            return jsonify({
                'success': False,
                'message': '用户无权限！',
                'data': None
            }), 403

        # 获取请求参数
        student_id = request.args.get('student_id')

        # 必填参数检查
        if not student_id:
            return jsonify({
                'success': False,
                'message': '学生ID不能为空',
                'data': None
            }), 400

        # 参数类型转换和验证
        try:
            student_id = int(student_id)
        except ValueError:
            return jsonify({
                'success': False,
                'message': '学生ID必须是整数',
                'data': None
            }), 400

        # 验证学生是否存在
        student = UserModel.query.get(student_id)
        if not student:
            return jsonify({
                'success': False,
                'message': '指定的学生不存在',
                'data': None
            }), 404

        # 查询支付记录并按时间降序排列
        payment_records = PaymentRecordModel.query.filter_by(
            student_id=student_id
        ).order_by(
            PaymentRecordModel.time.desc()
        ).all()

        # 构建返回数据
        records_list = []
        total_amount = 0.0

        for record in payment_records:
            record_info = {
                'payment_id': record.id,
                'course_id': record.course_id,
                'course_name': record.course_name,
                'amount': record.amount,
                'payment_time': record.time.strftime('%Y-%m-%d %H:%M:%S')
            }
            records_list.append(record_info)
            total_amount += record.amount

        return jsonify({
            'success': True,
            'message': '获取支付记录成功',
            'data': {
                'student_id': student_id,
                'total_records': len(records_list),
                'total_amount': round(total_amount, 2),
                'payment_records': records_list
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'服务器内部错误: {str(e)}',
            'data': None
        }), 500