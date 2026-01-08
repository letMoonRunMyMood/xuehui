from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

from . import register
from . import login
from . import captcha
from . import logout