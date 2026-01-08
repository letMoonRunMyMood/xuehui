from exts import db
from datetime import datetime


class CommentModel(db.Model):
    """评论存储模型

    用于存储评论。
    """
    __tablename__ = 'comment'  # 数据库表名

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
        comment='问评论ID，主键自增'
    )
    content = db.Column(
        db.Text,
        nullable=False,
        comment='评论内容'
    )
    image = db.Column(
        db.Text,
        nullable=True,
        default=None,
        comment='评论图片存储地址，可选'
    )
    created_at = db.Column(
        db.DateTime,
        default=datetime.now,
        nullable=False,
        comment='问题创建时间，默认为当前时间'
    )
    likes = db.Column(
        db.Integer,
        default=0,
        nullable=False,
        comment='问题点赞数，默认为0'
    )
    course_id = db.Column(
        db.Integer,
        index=True,
        comment='关联课程ID'
    )
    user_id = db.Column(
        db.Integer,
        default=None,
        comment='评论用户ID'
    )
    parent_id = db.Column(
        db.Integer,
        default=-1,
        comment='父评论ID，comment_type为1时取值为-1'
    )
    comment_type = db.Column(
        db.Integer,
        nullable=False,
        comment='评论类型，1为楼，2为层，3为对层的评论'
    )
