from exts import db
from datetime import datetime

class PlayProgressModel(db.Model):
    __tablename__ = 'play_progress'
    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
        comment='主键ID，自增'
    )
    user_id = db.Column(
        db.Integer,
        index=True,
        comment='用户ID'
    )
    video_id = db.Column(
        db.Integer,
        index=True,
        comment='视频ID'
    )
    progress = db.Column(
        db.Float,
        default=0.0,
        comment='播放进度'
    )
    last_updated = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now,
        comment='上次更新时间'
    )