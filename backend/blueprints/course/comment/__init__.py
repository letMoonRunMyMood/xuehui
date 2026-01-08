from flask import Blueprint

# 作为course_bp的子蓝图
comment_bp = Blueprint('comment', __name__)

from . import create_comment
from . import get_comments_by_course
from . import get_replies_by_comment
from . import like_comment
from . import delete_comment
# from . import create_reply
# from . import get_replies
# from . import delete_reply
# from . import report_comment
# from . import report_reply
# from . import like_reply

# from . import get_reports
# from . import delete_report