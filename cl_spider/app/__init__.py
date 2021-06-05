from concurrent.futures import ThreadPoolExecutor

from flask import Flask
from flask_babel import Babel
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from loguru import logger

logger.add('logs/server.log', enqueue=True)

executor = ThreadPoolExecutor(max_workers=4)


# create application
def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config.from_pyfile('config.py')

    return app


app = create_app()
db = SQLAlchemy(app)
babel = Babel(app)
bootstrap = Bootstrap(app)
