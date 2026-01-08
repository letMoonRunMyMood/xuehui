from exts import db


class ChapterModel(db.Model):
    """章节存储模型

    用于存储课程章节信息，包含章节标题和所属课程关联。
    """
    __tablename__ = 'chapter'  # 数据库表名

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
        comment='章节ID，主键自增'
    )
    title = db.Column(
        db.Text,
        nullable=False,
        comment='章节标题'
    )
    order = db.Column(
        db.Integer,
        nullable=False,
        comment='顺序'
    )

    course_id = db.Column(
        db.Integer,
        index=True,
        comment='所属课程ID'
    )



