from exts import db


class FavoritesModel(db.Model):
    """收藏关系模型

    用于存储学生收藏课程的多对多关系，记录学生与课程之间的收藏关系。
    """
    __tablename__ = 'favorites'  # 数据库表名

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
        comment='收藏记录ID，主键自增'
    )

    # 学生关联字段
    student_id = db.Column(
        db.Integer,
        index=True,
        comment='学生ID'
    )

    # 课程关联字段
    course_id = db.Column(
        db.Integer,
        index=True,
        comment='课程ID'
    )


