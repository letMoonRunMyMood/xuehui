from exts import db
from datetime import datetime


class CourseModel(db.Model):
    """课程存储模型

    用于存储平台课程信息，包含课程基本信息、教师关联和学科年级关联。
    """
    __tablename__ = 'course'  # 数据库表名

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
        comment='课程ID，主键自增'
    )
    name = db.Column(
        db.String(100),
        nullable=False,
        comment='课程名称'
    )
    cover = db.Column(
        db.Text,
        default='/static/default/default_cover.jpg',
        comment='封面URL路径，默认使用系统封面'
    )
    introduction = db.Column(
        db.Text,
        nullable=False,
        comment='课程简介'
    )
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now,
        comment='课程创建时间'
    )
    course_folder = db.Column(
        db.Text,
        nullable=False,
        comment='课程文件夹'
    )

    price = db.Column(
        db.Float,
        nullable=False,
        default=0.0,
        comment='订阅价格（单位：元）'
    )

    teacher_id = db.Column(
        db.Integer,
        index=True,
        comment='授课教师ID'
    )

    subject_id = db.Column(
        db.Integer,
        index=True,
        comment='所属学科ID'
    )

    grade_id = db.Column(
        db.Integer,
        index=True,
        comment='适用年级ID'
    )
