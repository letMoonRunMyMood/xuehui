from exts import db


class VideoModel(db.Model):
    """视频存储模型

    用于存储课程视频资源信息，包含视频标题、文件路径和所属章节关联。
    """
    __tablename__ = 'video'  # 数据库表名

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
        comment='视频ID，主键自增'
    )
    title = db.Column(
        db.String(100),
        nullable=False,
        comment='视频标题'
    )
    file = db.Column(
        db.Text,
        nullable=False,
        comment='视频文件存储路径'
    )
    order = db.Column(
        db.Integer,
        nullable=False,
        comment='顺序'
    )


    chapter_id = db.Column(
        db.Integer,
        nullable=False,
        index=True,
        comment='所属章节ID，外键关联chapter表'
    )
