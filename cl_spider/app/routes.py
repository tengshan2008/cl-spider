from concurrent.futures import ThreadPoolExecutor
from datetime import date

from cl_spider.app import app, db
from cl_spider.app.forms import (NovelsTaskForm, NovelTaskForm,
                                 PictureTaskForm, VideoTaskForm)
from cl_spider.app.models import Novel, Picture, Task
from cl_spider.config import (MINIO_SERVER_ENDPOINT, NOVEL_BUCKET_NAME,
                              PICTURE_BUCKET_NAME)
from cl_spider.spiders import video
from cl_spider.spiders.file_uploader import Uploader
from flask import redirect
from flask.helpers import flash, send_file
from flask_admin import Admin, BaseView, expose
from flask_admin.base import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.model import typefmt
from markupsafe import Markup


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
    title = getattr(model, 'title')
    pidx = getattr(model, 'pidx')
    date = getattr(model, 'public_datetime').strftime('%Y-%m')
    share = (f'http://{MINIO_SERVER_ENDPOINT}/{PICTURE_BUCKET_NAME}/'
             f'{date}/{title}/{pidx}')
    return Markup(f'<a href="{share}" target="_blank">Share</a>')


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
        date = getattr(model, 'public_datetime').strftime('%Y-%m')
        title = getattr(model, 'title')
        url = (f'http://{MINIO_SERVER_ENDPOINT}/{NOVEL_BUCKET_NAME}/'
               f'{date}/{title}.txt')
        return Markup(f'<a href="{url}" download="">Download</a>')

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
        'pidx': u'序号',
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


class TaskAdmin(CustomView):
    column_type_formatters = MY_DEFAULT_FORMATTERS
    # column_searchable_list = ('target', )
    column_labels = {
        'id': 'ID',
        'target': u'对象',
        'version': u'版本',
        'info': u'详细信息',
        'cost_time': u'耗时',
        'status': u'状态',
        'updated_at': u'更新日期'
    }
    column_list = list(column_labels.keys())
    column_default_sort = ('updated_at', True)
    can_set_page_size = True
    can_create, can_delete, can_edit = False, False, False

    def __init__(self, session, **kwargs):
        super().__init__(Task, session, **kwargs)


class NovelTaskView(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        from cl_spider.spiders.novel import IndexSpider, NovelSpider

        novel_form = NovelTaskForm()
        if novel_form.novel_submit.data and novel_form.validate_on_submit():
            if novel_form.url:
                spider = NovelSpider()
                executor = ThreadPoolExecutor(max_workers=1)
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
                executor = ThreadPoolExecutor(max_workers=1)
                executor.submit(lambda p: spider.get_latest(*p), args)
                flash(u'提交成功')
                return redirect('/admin/novel')
            else:
                flash(u'校验错误')

        return self.render('novel_task.html',
                           novel_form=novel_form,
                           novels_form=novels_form)


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
                executor = ThreadPoolExecutor(max_workers=1)
                executor.submit(spider.get_latest)
                flash(u'提交成功')
                return redirect('/admin/picture')
            else:
                flash(u'校验错误')

        return self.render('picture_task.html', form=form)


class VideoTaskView(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):

        form = VideoTaskForm()
        if form.validate_on_submit():
            if form.url:
                executor = ThreadPoolExecutor(max_workers=1)
                executor.submit(video.download, (form.url.data))
                flash(u'提交成功')
                return redirect('/admin/video')
            else:
                flash(u'校验错误')

        return self.render('video_task.html', form=form)


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
admin.add_view(TaskAdmin(db.session, name=u'任务'))
admin.add_view(NovelTaskView(name=u'小说', category=u'新建'))
admin.add_view(PictureTaskView(name=u'图片', category=u'新建'))
admin.add_view(VideoTaskView(name=u'视频', category=u'新建'))


def init_db():
    db.create_all()
