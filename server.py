from cl_spider.app import app
from cl_spider.app.main import init_db

app.debug = True

if __name__ == "__main__":
    init_db()
    app.run()
