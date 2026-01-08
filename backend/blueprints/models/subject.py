from exts import db


class SubjectModel(db.Model):
    """学科存储模型

    用于存储平台支持的学科分类信息，包含学科名称等基本信息。
    """
    __tablename__ = 'subject'  # 数据库表名

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
        comment='学科ID，主键自增'
    )
    name = db.Column(
        db.String(10),
        nullable=False,
        comment='学科名称，如：数学、语文、英语、物理、化学等'
    )
