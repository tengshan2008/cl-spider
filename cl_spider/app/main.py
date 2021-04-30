from flask import url_for, redirect
from flask.helpers import flash
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView

from flask_wtf import FlaskForm
from wtforms.fields.html5 import URLField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired
from cl_spider.app import app, db
from cl_spider.app.models import Novel, Picture


# Flask views
@app.route('/')
def index():
    return redirect('/admin')


# customized admin interface
class CustomView(ModelView):
    pass


class NovelAdmin(CustomView):
    column_searchable_list = ('title', )
    column_labels = {
        'origin_id': 'ID',
        'title': '标题',
        'author': '作者',
        'public_datetime': '发布日期',
        'category': '类别',
        'size': '字数',
        'created_at': '创建日期',
        'updated_at': '更新日期'
    }
    column_list = list(column_labels.keys())
    # column_details_list = ('path')
    # column_display_actions = ('create', 'update', 'delete')
    can_create, can_delete, can_edit = False, False, False

    def __init__(self, session, **kwargs):
        super().__init__(Novel, session, **kwargs)


class PictureAdmin(CustomView):
    column_searchable_list = ('title', )
    column_labels = {
        'origin_id': 'ID',
        'title': '标题',
        'author': '作者',
        'public_datetime': '发布日期',
    }
    column_list = list(column_labels.keys())
    can_create, can_delete, can_edit = False, False, False

    def __init__(self, session, **kwargs):
        super().__init__(Picture, session, **kwargs)


class NovelTaskView(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        return self.render('novel_task.html')


class PictureTaskForm(FlaskForm):
    url = URLField(label=u'网址：',
                   validators=[
                       DataRequired(message=u'网址不能为空'),
                   ])
    submit = SubmitField(u'提交')


class PictureTaskView(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        from cl_spider.spiders.picture import PictureSpider

        form = PictureTaskForm()
        if form.validate_on_submit():
            if form.url:
                spider = PictureSpider.load(set([form.url]))
                # spider.get_latest()
                flash("提交成功")
                return redirect('/admin/picture')
            else:
                flash("校验错误")

        return self.render('picture_task.html', form=form)


# create admin with custom base template
admin = Admin(app, 'CL-Spider', template_mode='bootstrap4')

admin.add_view(NovelAdmin(db.session, name='小说'))
admin.add_view(PictureAdmin(db.session, name='图片'))
admin.add_view(NovelTaskView(name='小说', category='新建'))
admin.add_view(PictureTaskView(name='图片', category='新建'))


def init_db():
    db.create_all()
