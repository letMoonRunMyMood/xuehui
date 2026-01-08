from exts import db
from datetime import datetime


class UserModel(db.Model):
    """学生存储模型

    用于存储用户信息，包含用户邮箱、用户名、密码、注册时间、头像和年级。
    """
    __tablename__ = 'user'  # 数据库表名

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
        comment='用户ID，主键自增'
    )
    email = db.Column(
        db.String(100),
        nullable=False,
        unique=True,
        index=True,
        comment='用户邮箱，唯一'
    )
    username = db.Column(
        db.String(100),
        nullable=False,
        comment='用户名'
    )
    password = db.Column(
        db.String(300),
        nullable=False,
        index=True,
        comment='加密后的密码'
    )
    join_time = db.Column(
        db.DateTime,
        default=datetime.now,
        comment='注册时间'
    )
    avatar = db.Column(
        db.Text,
        default='/static/default/default_avatar.jpg',
        comment='头像URL路径，默认使用系统头像'
    )
    role = db.Column(
        db.Integer,
        nullable=False,
        comment='用户身份，0为学生，1为讲师，2为管理员'
    )



