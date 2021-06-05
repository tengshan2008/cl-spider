from datetime import date
from cl_spider.app import app, db, executor
from cl_spider.app.models import Novel, Picture
from flask import redirect
from flask.helpers import flash, send_file
from flask_admin import Admin, BaseView, expose
from flask_admin.base import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.model import typefmt
from flask_wtf import FlaskForm
from markupsafe import Markup
from wtforms.fields.html5 import IntegerField, URLField
from wtforms.fields.simple import SubmitField, TextAreaField
from wtforms.validators import DataRequired


# Flask views
@app.route('/')
def index():
    return redirect('/admin')


# @app.route('/download/<text:title>', methods=['GET'])
# def download_blob(title):
#     _file = bytes()
#     return send_file(io.BytesIO(_file.blob),
#                      attachment_filename=_file.filename,
#                      mimetype=_file.mimetype)


def link_formatter(view, context, model, name):
    field = getattr(model, name)
    return Markup(f'<a href="{field}">LINK</a>')


def share_formatter(view, context, model, name):
    field = getattr(model, name)
    return Markup(f'<a href="{field}" target="_blank">SHARE</a>')


def date_format(view, value):
    return value.strftime('%Y-%m-%d %H:%M')


def title_format(view, content, model, name):
    title = getattr(model, name)
    if len(title) > 20:
        short = f'{title[:20]} ...'
        return Markup(f'<p title="{title}">{short}</p>')
    return Markup(f'<p>{title}</p>')


MY_DEFAULT_FORMATTERS = dict(typefmt.BASE_FORMATTERS)
MY_DEFAULT_FORMATTERS.update({
    date: date_format,
})


# customized admin interface
class CustomView(ModelView):
    pass


class NovelAdmin(CustomView):
    def __init__(self, session, **kwargs):
        super().__init__(Novel, session, **kwargs)

    def download_formatter(self, context, model, name):
        # url = self.get_url('download_blob', id=model.id)
        url = 'http://www.baidu.com'
        return Markup(f'<a href="{url}" target="_blank">Download</a>')

    column_type_formatters = MY_DEFAULT_FORMATTERS
    column_searchable_list = ('title', )
    column_labels = {
        'origin_id': 'ID',
        'title': u'标题',
        'author': u'作者',
        'public_datetime': u'发布日期',
        'category': u'类别',
        'link': u'链接',
        'size': u'字数',
        'updated_at': u'更新日期',
        'download': u'下载',
    }
    column_formatters = {
        'link': link_formatter,
        'title': title_format,
        'download': download_formatter,
    }
    column_list = list(column_labels.keys())
    column_default_sort = ('updated_at', True)
    can_set_page_size = True
    can_create, can_delete, can_edit = False, False, False


class PictureAdmin(CustomView):
    column_type_formatters = MY_DEFAULT_FORMATTERS
    column_searchable_list = ('title', )
    column_labels = {
        'id': 'ID',
        'origin_id': 'TID',
        'title': u'标题',
        'size': u'大小',
        'author': u'作者',
        'public_datetime': u'发布日期',
        'share': u'预览',
        'updated_at': u'更新日期',
    }
    column_formatters = {
        'share': share_formatter,
        'title': title_format,
    }
    column_list = list(column_labels.keys())
    column_default_sort = ('updated_at', True)
    can_set_page_size = True
    can_create, can_delete, can_edit = False, False, False

    def __init__(self, session, **kwargs):
        super().__init__(Picture, session, **kwargs)


class NovelTaskForm(FlaskForm):
    url = URLField(label=u'网址：',
                   validators=[
                       DataRequired(message=u'网址不能为空'),
                   ])
    novel_submit = SubmitField(u'提交')


class NovelsTaskForm(FlaskForm):
    url = URLField(label=u'网址：',
                   validators=[
                       DataRequired(message=u'网址不能为空'),
                   ])
    start_page = IntegerField(label=u'起始页码',
                              validators=[
                                  DataRequired(message=u'不能为空'),
                              ])
    end_page = IntegerField(label=u'终止页码',
                            validators=[
                                DataRequired(message=u'不能为空'),
                            ])
    novels_submit = SubmitField(label=u'提交')


class NovelTaskView(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        from cl_spider.spiders.novel import NovelSpider, IndexSpider

        novel_form = NovelTaskForm()
        if novel_form.novel_submit.data and novel_form.validate_on_submit():
            if novel_form.url:
                spider = NovelSpider()
                executor.submit(spider.get_latest, (novel_form.url.data))
                flash(u'提交成功')
                return redirect('/admin/novel')
            else:
                flash(u'校验错误')

        novels_form = NovelsTaskForm()
        if novels_form.novels_submit.data and novels_form.validate_on_submit():
            if novels_form.start_page and novels_form.end_page:
                spider = IndexSpider()
                args = [
                    novels_form.url.data,
                    novels_form.start_page.data,
                    novels_form.end_page.data,
                ]
                executor.submit(lambda p: spider.get_latest(*p), args)
                flash(u'提交成功')
                return redirect('/admin/novel')
            else:
                flash(u'校验错误')

        return self.render('novel_task.html',
                           novel_form=novel_form,
                           novels_form=novels_form)


class PictureTaskForm(FlaskForm):
    valida = [
        DataRequired(message=u'网址不能为空'),
    ]
    render_kw = {
        'class': 'form-control text-body',
        'rows': 10,
        'placeholder': '请输入网址，一行一条。',
    }
    url = TextAreaField(label=u'网址：', validators=valida, render_kw=render_kw)
    submit = SubmitField(u'提交')


class PictureTaskView(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        from cl_spider.spiders.picture import PictureSpider

        form = PictureTaskForm()
        if form.validate_on_submit():
            if form.url:
                urls = [
                    url.strip() for url in form.url.data.split('\n')
                    if url.strip()
                ]
                spider = PictureSpider.load(set(urls))
                executor.submit(spider.get_latest)
                flash(u'提交成功')
                return redirect('/admin/picture')
            else:
                flash(u'校验错误')

        return self.render('picture_task.html', form=form)


# create admin with custom base template
index_view = AdminIndexView(name=u'导航管理', template='index.html', url='/admin')
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



