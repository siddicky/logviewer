import os 
from functools import wraps

from motor.motor_asyncio import AsyncIOMotorClient
from sanic import Sanic, response
from sanic.exceptions import abort, NotFound, Unauthorized
from sanic_session import Session, InMemorySessionInterface

from jinja2 import Environment, PackageLoader

from objects import LogEntry

OAUTH2_CLIENT_ID = os.getenv('OAUTH2_CLIENT_ID')
OAUTH2_CLIENT_SECRET = os.getenv('OAUTH2_CLIENT_SECRET')


if OAUTH2_CLIENT_ID and OAUTH2_CLIENT_SECRET:
    using_oauth = True

app = Sanic(__name__)
Session(app, interface=InMemorySessionInterface())

app.static('/static', './static')


def authrequired():
    def decorator(func):
        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            if using_oauth and not request['session'].get('logged_in'):
                abort(401)
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator


jinja_env = Environment(loader=PackageLoader('app', 'templates'))


def render_template(name, *args, **kwargs):
    template = jinja_env.get_template(name + '.html')
    kwargs.update(globals())
    return response.html(template.render(*args, **kwargs))


app.render_template = render_template


@app.listener('before_server_start')
async def init(app, loop):
    app.db = AsyncIOMotorClient(os.getenv('MONGO_URI')).modmail_bot

@app.exception(NotFound)
async def not_found(request, exc):
    return render_template('not_found')

@app.exception(Unauthorized)
async def not_found(request, exc):
    return render_template('unauthorized')


@app.get('/')
async def index(request):
    return render_template('index')


@app.get('/logs/raw/<key>')
@authrequired()
async def get_raw_logs_file(request, key):
    document = await app.db.logs.find_one({'key': key})

    if document is None:
        return response.text('Not Found', status=404)

    log_entry = LogEntry(app, document)

    return log_entry.render_plain_text()


@app.get('/logs/<key>')
@authrequired()
async def get_logs_file(request, key):
    """Returned the plain text rendered log entry"""

    document = await app.db.logs.find_one({'key': key})

    if document is None:
        return response.text('Not Found', status=404)

    log_entry = LogEntry(app, document)

    return log_entry.render_html()


@app.get('/favicon.ico')
async def get_favicon(request):
    return await response.file('/static/favicon.ico')

if __name__ == '__main__':
    app.run(
        host=os.getenv('HOST', '0.0.0.0'), 
        port=os.getenv('PORT', 8000),
        debug=bool(os.getenv('DEBUG', False))
        )
