from datetime import datetime
from exts import db

class InvitationCodeModel(db.Model):
    """邀请码模型

    用于存储邀请码信息，包含被邀请用户邮箱、邀请码、邀请码创建时间
    """
    __tablename__ = 'invitation_code'
    id=db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
        comment='主键ID，自增'
    )
    email = db.Column(
        db.String(100),
        nullable=False,
        comment='用户邮箱地址，不可为空'
    )
    invitation_code = db.Column(
        db.String(10),
        nullable=False,
        comment='10位邀请码，不可为空'
    )
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        comment='邀请码创建时间'
    )