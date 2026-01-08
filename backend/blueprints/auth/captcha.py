import string
import random
from flask import request, jsonify
from . import auth_bp
from flask_mail import Message
from exts import mail
from blueprints.models.email_captcha_memory import EmailCaptchaMemoryStorage

# /auth/captcha
@auth_bp.get('/captcha')
def get_email_captcha():
    try:
        email = request.args.get('email')
        if not email:
            return jsonify({
                "success": False,
                "message": "邮箱地址不能为空"
            }), 400

        source = string.digits * 4
        captcha = ''.join(random.sample(source, 4))

        message = Message(
            subject="帅otto！冲刺，冲！♿",
            recipients=[email],
            body=f"您的验证码是: {captcha}"
        )
        mail.send(message)

        # 存储验证码到内存
        EmailCaptchaMemoryStorage.add_captcha(email, captcha)

        return jsonify({
            "success": True,
            "message": "成功发送验证码"
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500