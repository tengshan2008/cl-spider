from concurrent.futures import ThreadPoolExecutor

from flask import Flask
from flask_babel import Babel
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

executor = ThreadPoolExecutor(max_workers=2)
# create application
app = Flask(__name__, template_folder='templates')

app.config.from_pyfile('config.py')

db = SQLAlchemy(app)
babel = Babel(app)
bootstrap = Bootstrap(app)
