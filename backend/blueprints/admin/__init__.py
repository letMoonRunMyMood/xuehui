from flask import Blueprint

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

from . import create_code
from . import get_code
from . import delete_code
from . import create_advertisement
from . import  get_advertisement
from . import delete_advertisement
from . import statistics