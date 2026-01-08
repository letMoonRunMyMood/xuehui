from exts import db

class StudentInformationModel(db.Model):
    __tablename__ = 'student_information'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
        comment='学生信息ID，主键自增'
    )
    student_id = db.Column(
        db.Integer,
        nullable=False,
        comment='学生ID'
    )
    grade = db.Column(
        db.String(20),
        nullable=True,
        comment='学生年级，如：六年级、初一、高三等'
    )