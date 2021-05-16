from concurrent.futures import ThreadPoolExecutor
import threading

from flask import Flask
from flask_babel import Babel
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from loguru import logger

logger.add('logs/server.log', enqueue=True)

executor = ThreadPoolExecutor(max_workers=4)
# create application
app = Flask(__name__, template_folder='templates')

app.config.from_pyfile('config.py')

db = SQLAlchemy(app)
babel = Babel(app)
bootstrap = Bootstrap(app)

thread_lock = threading.Lock()
