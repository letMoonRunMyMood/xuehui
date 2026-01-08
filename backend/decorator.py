from functools import wraps
from flask import jsonify, g

def login_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if g.user:
            return func(*args, **kwargs)
        else:
            return jsonify({
                "success":False,
                "message":"未登录！",
                "data":None
            }),401
    return inner