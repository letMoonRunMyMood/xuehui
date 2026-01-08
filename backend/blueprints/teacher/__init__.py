from flask import Blueprint

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')

from . import get_created_course
from . import get_teacher_info
from . import update_teacher_info