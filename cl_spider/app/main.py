from flask import url_for
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView

from cl_spider.app import app, db
from cl_spider.app.models import Novel, Picture



# Flask views
@app.route('/')
def index():
    return url_for('admin.index')
    # return '<a href="/admin/">Click me to get to Admin!</a>'

class IndexView(BaseView):
    @expose('/')
    def index(self):
        return self.render('index.html')


class TaskView(BaseView):
    @expose('/')
    def index(self):
        return self.render('index.html')

    @expose('/task/novel')
    def novel(self):
        return self.render('task_novel.html')

    @expose('/task/picture')
    def picture(self):
        return self.render('task_picture.html')


# customized admin interface
class CustomView(ModelView):
    pass


class NovelAdmin(CustomView):
    column_searchable_list = ('title',)
    column_list = ('origin_id', 'title', 'author', 'public_datetime',
                   'category', 'size', 'created_at', 'updated_at')
    # column_details_list = ('path')
    column_labels = {'origin_id': 'ID', 'title': '标题', 'author': '作者',
                     'public_datetime': '发布日期', 'category': '类别',
                     'size': '字数', 'created_at': '创建日期',
                     'updated_at': '更新日期'}
    # column_display_actions = ('create', 'update', 'delete')
    can_create, can_delete, can_edit = False, False, False


class PictureAdmin(CustomView):
    column_searchable_list = ('title',)
    column_list = ('origin_id', 'title', 'author', 'public_datetime')


# create admin with custom base template
admin = Admin(app, 'CL-Spider', template_mode='bootstrap4')

# admin.add_view(IndexView(name='Hello', endpoint='/'))
# admin.add_view(TaskView(name='Task'))
admin.add_view(
    TaskView(name='Novel', endpoint='/task/novel', category='Task'))
admin.add_view(
    TaskView(name='Picture', endpoint='/task/picture', category='Task'))
admin.add_view(NovelAdmin(Novel, db.session))
admin.add_view(PictureAdmin(Picture, db.session))


def init_db():
    db.drop_all()
    db.create_all()
