# create in-memory database
DATABASE_FILE = 'db.sqlite'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_FILE
SQLALCHEMY_ECHO = True
SQLALCHEMY_TRACK_MODIFICATIONS = False

# secret key
SECRET_KEY = 'very very hard to guess token'

# babel
BABEL_DEFAULT_LOCALE = 'zh_CN'

# theme
BOOTSTRAP_BOOTSWATCH_THEME = 'lumen'
