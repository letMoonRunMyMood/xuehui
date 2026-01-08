from flask import Blueprint

course_bp = Blueprint('course', __name__, url_prefix='/course')

from .comment import comment_bp
course_bp.register_blueprint(comment_bp, url_prefix='/comment')

from . import create_course
from . import update_course
from . import create_chapter
from . import update_chapter
from . import upload_video
from . import upload_document
from . import delete_video
from . import delete_document
from . import delete_chapter
# from . import delete_course
from . import get_course
from . import get_course_detail
from . import get_video
from . import get_document
from . import save_progress
from . import get_progress
from . import search_courses
from . import recommend