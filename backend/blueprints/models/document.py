from exts import db


class DocumentModel(db.Model):
    """文档存储模型

    用于存储课程文档资料信息，包含文档标题、文件路径和所属章节关联。
    """
    __tablename__ = 'document'  # 数据库表名

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
        comment='文档ID，主键自增'
    )
    title = db.Column(
        db.String(100),
        nullable=False,
        comment='文档标题'
    )
    file = db.Column(
        db.Text, nullable=False,
        comment='文档文件存储路径'
    )
    chapter_id = db.Column(
        db.Integer,
        index=True,
        comment='所属章节ID'
    )
