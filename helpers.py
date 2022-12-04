from flask import redirect, render_template, request, session
from functools import wraps
import re

# Login Required Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

# Format amount as USD
def usd(amount):
    return f"${amount:,.2f}"

 # This functions checks if the password meets all the requirements
def validate(password):

    if len(password) < 8:
        return False
    elif re.search('[0-9]', password) is None:
        return False
    elif re.search('[A-Z]', password) is None:
        return False

    return True