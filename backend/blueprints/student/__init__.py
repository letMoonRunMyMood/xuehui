from flask import Blueprint

student_bp = Blueprint('student', __name__, url_prefix='/student')

from . import get_student_info
from . import update_student_info
from . import create_subscribe
from . import cancel_subscribe
from . import check_subscribe
from . import get_subscribed_course
from . import create_favorite
from . import cancel_favorite
from . import check_favorite
from . import get_favorite_course
from . import get_payment_records


