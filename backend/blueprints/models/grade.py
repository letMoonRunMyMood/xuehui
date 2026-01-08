from exts import db


class GradeModel(db.Model):
    """年级存储模型

    用于存储学生年级信息，包含年级名称等基本信息。
    """
    __tablename__ = 'grade'  # 数据库表名

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
        comment='年级ID，主键自增'
    )
    name = db.Column(
        db.String(10),
        nullable=False,
        comment='年级名称，如：一年级、初二、高三等'
    )