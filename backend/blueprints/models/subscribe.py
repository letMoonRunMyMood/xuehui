from exts import db


class SubscribeModel(db.Model):
    """课程订阅关系模型

    用于存储学生订阅课程的多对多关系，记录学生与课程之间的订阅关系。
    """
    __tablename__ = 'subscribe'  # 数据库表名

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
        comment='订阅记录ID，主键自增'
    )

    # 学生关联字段
    student_id = db.Column(
        db.Integer,
        index=True,
        comment='订阅学生ID'
    )

    # 课程关联字段
    course_id = db.Column(
        db.Integer,
        index=True,
        comment='被订阅课程ID'
    )
