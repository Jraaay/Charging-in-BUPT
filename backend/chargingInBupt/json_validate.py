from jsonschema import validate, ValidationError
from sanic import json


def json_validate(schema):
    def wrapper(func):
        def inner(request, *args, **kwargs):
            json_body = None
            try:
                json_body = request.json
            except Exception:
                return json({
                    "code": -1,
                    "message": "Invalid request"
                })
            if json_body is None:
                return json({
                    "code": -1,
                    "message": "Invalid request"
                })
            try:
                validate(json_body, schema)
            except ValidationError as e:
                return json({
                    "code": -1,
                    "message": "Invalid request"
                })
            else:
                return func(request, *args, **kwargs)
        return inner
    return wrapper