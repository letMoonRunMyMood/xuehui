from exts import db
from datetime import datetime

class LikeModel(db.Model):
    """点赞记录模型（支持评论和回复）"""
    __tablename__ = 'like'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
        comment='点赞记录ID'
    )
    comment_id = db.Column(
        db.Integer,
        nullable=False,
        comment='评论ID'
    )
    user_id = db.Column(
        db.Integer,
        nullable=False,
        comment='用户ID'
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.now,
        comment='点赞时间'
    )

    __table_args__ = (
        db.Index('idx_user_comment', 'user_id', 'comment_id', unique=True),
    )
