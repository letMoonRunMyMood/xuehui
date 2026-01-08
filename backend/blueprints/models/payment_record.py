from exts import db
from datetime import datetime


class PaymentRecordModel(db.Model):
    """支付记录存储模型

    用于存储学生购买课程的支付记录，包含课程关联、学生关联、支付金额和时间等信息。
    """
    __tablename__ = 'payment_record'  # 数据库表名

    id = db.Column(
        db.String(100),
        primary_key=True,
        comment='支付记录ID，主键'
    )

    # 课程关联字段
    course_id = db.Column(
        db.Integer,
        comment='课程ID'
    )

    course_name = db.Column(
        db.String(100),
        nullable=False,
        comment='课程名称'
    )

    # 学生关联字段
    student_id = db.Column(
        db.Integer,
        index=True,
        comment='学生ID'
    )

    amount = db.Column(
        db.Float,
        nullable=False,
        comment='支付金额（单位：元）'
    )
    time = db.Column(
        db.DateTime,
        default=datetime.now,
        nullable=False,
        comment='支付时间，默认为当前时间'
    )
