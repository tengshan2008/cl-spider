from datetime import date

from cl_spider.app import app, db, executor
from cl_spider.app.models import Novel, Picture
from flask import redirect
from flask.helpers import flash
from flask_admin import Admin, BaseView, expose
from flask_admin.base import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.model import typefmt
from flask_wtf import FlaskForm
from markupsafe import Markup
from wtforms.fields.html5 import URLField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired


# Flask views
@app.route('/')
def index():
    return redirect('/admin')


def share_link_formatter(view, context, model, name):
    field = getattr(model, name)
    return Markup(f'<a href="{field}">LINK</a>')


def date_format(view, value):
    return value.strftime('%Y-%m-%d %H:%M:%S')


MY_DEFAULT_FORMATTERS = dict(typefmt.BASE_FORMATTERS)
MY_DEFAULT_FORMATTERS.update({
    date: date_format,
})


# customized admin interface
class CustomView(ModelView):
    pass


class NovelAdmin(CustomView):
    column_searchable_list = ('title', )
    column_labels = {
        'origin_id': 'ID',
        'title': u'标题',
        'author': u'作者',
        'public_datetime': u'发布日期',
        'category': u'类别',
        'size': u'字数',
        'created_at': u'创建日期',
        'updated_at': u'更新日期',
    }
    column_list = list(column_labels.keys())
    # column_details_list = ('path')
    # column_display_actions = ('create', 'update', 'delete')
    can_create, can_delete, can_edit = False, False, False

    def __init__(self, session, **kwargs):
        super().__init__(Novel, session, **kwargs)


class PictureAdmin(CustomView):
    column_type_formatters = MY_DEFAULT_FORMATTERS
    column_searchable_list = ('title', )
    column_labels = {
        'id': 'ID',
        'origin_id': 'TID',
        'title': u'标题',
        'author': u'作者',
        'public_datetime': u'发布日期',
        'share': u'预览',
        'updated_at': u'更新日期',
    }
    column_formatters = {'share': share_link_formatter}
    column_list = list(column_labels.keys())
    column_default_sort = ('updated_at', True)
    can_set_page_size = True
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
    # @run_async
    # async def index(self):
    def index(self):
        from cl_spider.spiders.picture import PictureSpider

        form = PictureTaskForm()
        if form.validate_on_submit():
            if form.url:
                spider = PictureSpider.load(set(form.url.raw_data))
                executor.submit(spider.get_latest)
                flash(u'提交成功')
                return redirect('/admin/picture')
            else:
                flash(u'校验错误')

        return self.render('picture_task.html', form=form)


# create admin with custom base template
index_view = AdminIndexView(name=u'导航栏', template='index.html', url='/admin')
admin = Admin(
    app,
    'CL-Spider',
    index_view=index_view,
    template_mode='bootstrap4',
)

admin.add_view(NovelAdmin(db.session, name=u'小说'))
admin.add_view(PictureAdmin(db.session, name=u'图片'))
admin.add_view(NovelTaskView(name=u'小说', category=u'新建'))
admin.add_view(PictureTaskView(name=u'图片', category=u'新建'))


def init_db():
    db.create_all()
