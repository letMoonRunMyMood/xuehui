import json

from flask import request, jsonify, redirect
from blueprints.pay import pay_bp
from exts import logger, alipay_client


@pay_bp.get('/pay_return')
def pay_return():
    try:
        # ===================== 调试步骤1：标记函数开始执行，打印完整请求参数 =====================
        print("=" * 50 + " 开始处理 /pay_return 回调 " + "=" * 50)
        # 获取所有GET请求参数
        data = request.args.to_dict()
        print(f"【调试1-完整请求参数】支付宝传递的所有参数：\n{data}")
        print(f"【调试1-参数类型】data 类型：{type(data)}，参数长度：{len(data)}")

        # ===================== 调试步骤2：打印待验签的参数副本，标记验签开始 =====================
        data_copy = data.copy()
        print(f"【调试2-待验签参数副本】传递给验签方法的参数：\n{data_copy}")
        print("【调试3-开始验签】正在调用 alipay_client.verify_sandbox_notify() 进行验签...")

        # 执行验签
        verify_result = alipay_client.verify_sandbox_notify(data_copy)
        
        # ===================== 调试步骤3：打印验签结果 =====================
        print(f"【调试4-验签结果】验签是否通过：{verify_result}（True=通过，False=不通过）")

        if verify_result:
            # ===================== 调试步骤4：验签通过，分步解析 body 参数 =====================
            # 1. 提取原始 body 数据并打印
            raw_body = data.get('body')
            print(f"【调试5-原始body】从参数中提取的 body 原始值：\n{raw_body}")
            print(f"【调试5-body类型】raw_body 类型：{type(raw_body)}")

            # 2. 解析 JSON 格式的 body 并打印
            parsed_body = json.loads(raw_body)
            print(f"【调试6-解析后body】JSON 解析后的 body 数据：\n{parsed_body}")
            print(f"【调试6-body类型】parsed_body 类型：{type(parsed_body)}")

            # 3. 提取 base_url 并打印
            base_url = parsed_body['base_url']
            print(f"【调试7-跳转地址】提取的 base_url 目标地址：\n{base_url}")
            print(f"【调试7-地址类型】base_url 类型：{type(base_url)}")

            # ===================== 调试步骤5：标记即将重定向，打印最终跳转信息 =====================
            print(f"【调试8-即将跳转】准备重定向到前端地址：{base_url}")
            print("=" * 50 + " /pay_return 回调处理完成（即将跳转） " + "=" * 50)
            
            # 执行重定向
            return redirect(base_url)
        
        # ===================== 调试步骤6：验签不通过，打印详细信息并返回响应 =====================
        else:
            print("【调试9-验签失败】alipay_client.verify_sandbox_notify() 返回 False，验签不通过！")
            print(f"【调试9-失败详情】当前验签参数：\n{data_copy}")
            print("=" * 50 + " /pay_return 回调处理完成（验签失败） " + "=" * 50)
            
            # 补全返回响应，避免 TypeError
            logger.error("支付返回回调验签不通过")
            return jsonify({
                'success': False,
                'message': '支付返回回调验签不通过'
            }), 400

    except Exception as e:
        # ===================== 调试步骤7：捕获异常，打印完整异常信息 =====================
        print("=" * 50 + " /pay_return 回调处理异常 " + "=" * 50)
        print(f"【调试10-异常类型】异常类型：{type(e).__name__}")
        print(f"【调试10-异常信息】异常详细信息：{str(e)}")
        print(f"【调试10-当前参数】异常发生时的请求参数：\n{request.args.to_dict()}")
        print("=" * 50 + " /pay_return 回调异常结束 " + "=" * 50)
        
        # 记录异常日志并返回响应
        logger.error(f"支付返回处跳转异常: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'处理失败: {str(e)}'
        }), 500