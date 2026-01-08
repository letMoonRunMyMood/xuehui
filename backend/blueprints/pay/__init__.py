from flask import Blueprint

pay_bp = Blueprint('pay', __name__, url_prefix='/pay')

from . import create_order
from . import pay_return
from . import query_sandbox_order
from . import pay_notify