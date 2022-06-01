import jwt
from functools import wraps


from sanic import json

from chargingInBupt.orm import session, User
from chargingInBupt.config import CONFIG


def generate_token(username, is_admin):
    return jwt.encode({'username': username, 'role': 'ADMIN' if is_admin else 'USER'}, CONFIG['JWT']['secret'], algorithm='HS256')


def authorized():
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            is_authorized = False

            token = request.headers.get('Authorization').split(' ')[1]
            try:
                payload = jwt.decode(
                    token, CONFIG['JWT']['secret'], algorithms=['HS256'])
                is_authorized = True
            except jwt.InvalidTokenError:
                pass

            if is_authorized:
                response = await f(request, *args, **kwargs)
                return response
            else:
                return json({"status": "not_authorized"}, 403)
        return decorated_function
    return decorator


def authorized_admin():
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            is_authorized = False
            is_admin = False

            token = request.headers.get('Authorization').split(' ')[1]
            try:
                payload = jwt.decode(
                    token, CONFIG['JWT']['secret'], algorithms=['HS256'])
                is_admin = session.query(User).filter(
                    User.username == payload['username']).first().admin
                is_authorized = True
            except jwt.InvalidTokenError:
                pass

            if is_authorized and is_admin:
                response = await f(request, *args, **kwargs)
                return response
            else:
                return json({"status": "not_authorized"}, 403)
        return decorated_function
    return decorator


def get_username(request):
    token = request.headers.get('Authorization').split(' ')[1]
    try:
        payload = jwt.decode(
            token, CONFIG['JWT']['secret'], algorithms=['HS256'])
        return payload['name']
    except jwt.InvalidTokenError:
        return ""
