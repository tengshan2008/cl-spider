from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_babelex import Babel
from flask_bootstrap import Bootstrap

# create application
app = Flask(__name__, template_folder='templates')

app.config.from_pyfile('config.py')

app.config['DATABASE_FILE'] = 'db.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    app.config['DATABASE_FILE']
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = 'very very hard to guess token'
app.config['BABEL_DEFAULT_LOCALE'] = 'zh_CN'

db = SQLAlchemy(app)
babel = Babel(app)
bootstrap = Bootstrap(app)
