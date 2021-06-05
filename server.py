from cl_spider.app import app
from cl_spider.app.routes import init_db

if __name__ == "__main__":
    init_db()
    app.run(debug=False, use_reloader=False)
