from flask import session, abort, current_app
from functools import wraps

# @login_required decorator
def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if session.get('profile') is None:
            abort(401)
        return func(*args, **kwargs)
    return decorated_view
