from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from tools.alipay_client import AlipayClient
import logging

db=SQLAlchemy()
mail=Mail()
cors = CORS()
logging.basicConfig(level=logging.INFO)
alipay_client = AlipayClient()
logger = logging.getLogger(__name__)