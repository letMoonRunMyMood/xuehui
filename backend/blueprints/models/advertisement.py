from exts import db


class AdvertisementModel(db.Model):
    """广告存储模型

    用于存储平台广告信息，包含广告链接、图片和名称。
    """
    __tablename__ = 'advertisement'  # 数据库表名

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
        comment='广告ID，主键自增'
    )
    link = db.Column(
        db.Text,
        nullable=False,
        comment='广告跳转链接'
    )
    image = db.Column(
        db.Text,
        nullable=False,
        comment='广告图片存储路径'
    )
    name = db.Column(
        db.String(100),
        nullable=False,
        comment='广告名称'
    )