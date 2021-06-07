# create in-memory database
# DATABASE_FILE = 'db.sqlite'
# SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_FILE
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False

# create mysql database
DIALECT = 'mysql'
DRIVER = 'pymysql'
USERNAME = 'root'
PASSWORD = '123456'
HOST = 'mysql'
# HOST = '192.168.1.5'
PORT = '3306'
DATABASE = 'cl'

SQLALCHEMY_DATABASE_URI = f'{DIALECT}+{DRIVER}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}?charset=utf8mb4'

# secret key
SECRET_KEY = 'very very hard to guess token'

# babel
BABEL_DEFAULT_LOCALE = 'zh_CN'

# theme
BOOTSTRAP_BOOTSWATCH_THEME = 'lumen'
