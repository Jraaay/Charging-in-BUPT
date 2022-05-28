import jwt
from functools import wraps


from sanic import json

from chargingInBupt.orm import session, User
from chargingInBupt.config import CONFIG


def generate_token(id, username):
    return jwt.encode({'username': username, 'id': id}, CONFIG['JWT']['secret'], algorithm='HS256')


def authorized():
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            is_authorized = False

            token = request.headers.get('Authorization').split(' ')[1]
            try:
                payload = jwt.decode(token, CONFIG['JWT']['secret'], algorithms=['HS256'])
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
                payload = jwt.decode(token, CONFIG['JWT']['secret'], algorithms=['HS256'])
                is_admin = session.query(User).filter(
                    User.id == payload['id']).first().admin
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
        payload = jwt.decode(token, CONFIG['JWT']['secret'], algorithms=['HS256'])
        return payload['name']
    except jwt.InvalidTokenError:
        return ""