from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# create application
app = Flask(__name__, template_folder='templates')

app.config.from_pyfile('config.py')

app.config['DATABASE_FILE'] = 'db.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    app.config['DATABASE_FILE']
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
