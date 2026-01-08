from pydantic import BaseModel, EmailStr, validator
import re

# Pydantic 验证模型
class RegisterModel(BaseModel):
    email: EmailStr
    username: str
    password: str
    password_confirm: str

    @validator('username')
    def username_length(cls, v):
        if len(v) < 2 or len(v) > 10:
            raise ValueError('用户名长度必须在2-10个字符之间')

        # 中文、字母、数字验证
        if not re.fullmatch(r'^[\u4e00-\u9fa5a-zA-Z0-9]+$', v):
            raise ValueError('用户名只能包含中文、字母和数字')

        return v

    @validator('password')
    def password_length(cls, v):
        if len(v) < 6 or len(v) > 20:
            raise ValueError('密码长度必须在6-20个字符之间')

        # 检查是否包含至少一个大写和小写字母
        if (not re.search(r'[A-Z]', v)
                or  not re.search(r'[a-z]', v)
                or not re.search(r'[0-9]', v)):
            raise ValueError('密码必须包含至少一个大写字母、小写字母和数字')

        return v

    @validator('password_confirm')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('两次密码不一致')
        return v
