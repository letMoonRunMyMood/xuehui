from datetime import datetime
from flask import request, jsonify
from werkzeug.security import generate_password_hash
from exts import db
from . import auth_bp
from .Form.RegisterForm import RegisterModel
from blueprints.models.user import UserModel
from blueprints.models.invitation_code import InvitationCodeModel
from blueprints.models.email_captcha_memory import EmailCaptchaMemoryStorage
from pydantic import ValidationError

from ..models.student_information import StudentInformationModel
from ..models.teacher_information import TeacherInformationModel


# /auth/register
@auth_bp.post('/register')
def register():
    try:
        # 验证输入数据
        user_data = request.form.to_dict()
        role = int(user_data['role'])
        email = user_data['email']
        username = user_data['username']
        register_data = RegisterModel(**user_data)

        # 禁止注册管理员
        # if role == 2:
        #     return jsonify({
        #         "success": False,
        #         "message": "无法注册管理员"
        #     }), 400

        # 检查邮箱是否已存在
        if (UserModel.query.filter_by(email=register_data.email).first()):
            return jsonify({
                "success": False,
                "message": "该邮箱已被注册！"
            }), 400

        # 检查用户名是否已存在
        if (UserModel.query.filter_by(username=username).first()):
            return jsonify({
                "success": False,
                "message": "该用户名已被使用！"
            }), 400

        # 检查验证码是否正确
        # captcha = user_data['captcha']
        # if not EmailCaptchaMemoryStorage.is_valid(email, captcha):
        #     return jsonify({
        #         "success": False,
        #         "message": "验证码错误或已过期！"
        #     }), 400

        # 验证通过后删除验证码
        EmailCaptchaMemoryStorage.delete_captcha(email)

        # 检查讲师注册时验证邀请码是否正确
        # if role == 1:
        #     invitation_code = user_data['invitation_code']
        #     invitation_code_model = InvitationCodeModel.query.filter_by(email=email).first()
        #     if not invitation_code_model or invitation_code != invitation_code_model.invitation_code:
        #         return jsonify({
        #             "success": False,
        #             "message": "邀请码错误！"
        #         }), 400
        #     else:
        #         db.session.delete(invitation_code_model)
        #         db.session.commit()

        # 创建用户
        user = UserModel(
            email=register_data.email,
            username=register_data.username,
            password=generate_password_hash(register_data.password),
            join_time=datetime.now(),
            role=role
        )

        db.session.add(user)
        db.session.flush()

        # 根据角色在对应的信息表中添加记录
        if role == 0:  # 学生
            student_info = StudentInformationModel(
                student_id=user.id,  # 使用刚创建的用户ID
                grade=None  # 其他字段为空
            )
            db.session.add(student_info)
        elif role == 1:  # 教师
            teacher_info = TeacherInformationModel(
                teacher_id=user.id,  # 使用刚创建的用户ID
                university=None,  # 其他字段为空
                introduction=None
            )
            db.session.add(teacher_info)

        # 提交所有更改
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "注册成功"
        }), 200

    except ValidationError as e:
        # 提取Pydantic验证错误中的中文信息
        errors = e.errors()
        if errors and len(errors) > 0:
            # 获取第一个错误的中文信息
            error_msg = errors[0].get('msg', '')
            # 提取中括号中的中文描述
            import re
            chinese_msg = re.search(r'[\u4e00-\u9fa5]+.*[\u4e00-\u9fa5]+', error_msg)
            if chinese_msg:
                error_msg = chinese_msg.group(0)
            return jsonify({
                "success": False,
                "message": error_msg
            }), 400
        return jsonify({
            "success": False,
            "message": "验证错误"
        }), 400

    except Exception as e:
        # 处理其他错误
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"注册失败，请稍后再试: {str(e)}"
        }), 500