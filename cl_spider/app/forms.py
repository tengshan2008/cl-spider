from flask_wtf import FlaskForm
from wtforms.fields.html5 import IntegerField, URLField
from wtforms.fields.simple import SubmitField, TextAreaField
from wtforms.validators import DataRequired


class NovelTaskForm(FlaskForm):
    url = URLField(label=u'网址：', validators=[DataRequired(message=u'网址不能为空')])
    novel_submit = SubmitField(u'提交')


class NovelsTaskForm(FlaskForm):
    valida = [DataRequired(message=u'网址不能为空')]
    url = URLField(label=u'网址：', validators=valida)
    valida = [DataRequired(message=u'不能为空')]
    start_page = IntegerField(label=u'起始页码', validators=valida)
    valida = [DataRequired(message=u'不能为空')]
    end_page = IntegerField(label=u'终止页码', validators=valida)
    novels_submit = SubmitField(label=u'提交')


class PictureTaskForm(FlaskForm):
    valida = [DataRequired(message=u'网址不能为空')]
    render_kw = {
        'class': 'form-control text-body',
        'rows': 10,
        'placeholder': '请输入网址，一行一条。',
    }
    url = TextAreaField(label=u'网址：', validators=valida, render_kw=render_kw)
    submit = SubmitField(u'提交')


class VideoTaskForm(FlaskForm):
    valida = [DataRequired(message=u'网址不能为空')]
    url = URLField(label=u'视频网址：', validators=valida)
    render_kw = {'placeholder': '60'}
    clip_length = IntegerField(label=u'分段时长', render_kw=render_kw)
    # preview = ''
    submit = SubmitField(u'提交')
