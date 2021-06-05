from cl_spider.app import app
from cl_spider.app import routes

if __name__ == "__main__":
    routes.init_db()
    app.run(debug=False, use_reloader=False)
