from exts import db

class TeacherInformationModel(db.Model):
    __tablename__ = 'teacher_information'
    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
        comment='讲师信息ID，主键自增'
    )
    teacher_id = db.Column(
        db.Integer,
        nullable=False,
        comment='讲师ID'
    )
    university = db.Column(
        db.String(20),
        nullable=True,
        comment='毕业院校'
    )
    introduction = db.Column(
        db.Text,
        nullable=True,
        comment='自我介绍'
    )