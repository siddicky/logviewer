from functools import wraps
from sanic.exceptions import abort
import inspect


def get_stack_variable(name):
    stack = inspect.stack()
    try:
        for frames in stack:
            try:
                frame = frames[0]
                current_locals = frame.f_locals
                if name in current_locals:
                    return current_locals[name]
            finally:
                del frame
    finally:
        del stack

def authrequired():
    def decorator(func):
        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            if request.app.using_oauth and not request['session'].get('logged_in'):
                abort(401)
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator