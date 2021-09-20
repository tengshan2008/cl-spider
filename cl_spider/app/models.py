from cl_spider.app import db
from datetime import datetime


# Models
class Novel(db.Model):
    __tablename__ = 'novel'
    id = db.Column(db.Integer, primary_key=True)
    origin_id = db.Column(db.String(255), default='UNKNOW')
    title = db.Column(db.String(255), default='UNKNOW')
    author = db.Column(db.String(255), nullable=True)
    public_datetime = db.Column(db.DateTime, nullable=True)
    category = db.Column(db.String(255), nullable=True)
    link = db.Column(db.String(255), nullable=True)
    size = db.Column(db.Integer, default=0)
    task_id = db.Column(db.String(255), nullable=True)
    status = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now)
    deleted_at = db.Column(db.DateTime)

    def __unicode__(self):
        return self.title

    def __repr__(self):
        return f"<Novel {self.title}>"


class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(255))
    target = db.Column(db.String(255))
    version = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __unicode__(self):
        return self.task_id

    def __repr__(self):
        return f'<task {self.task_id}>'


class PictureTask(db.Model):
    __tablename__ = 'picture_task'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(255))
    link = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __unicode__(self):
        return self.id

    def __repr__(self):
        return f'<picture_task {self.id}>'


class NovelIndexTask(db.Model):
    __tablename__ = 'novel_index_task'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(255))
    start_index = db.Column(db.Integer)
    end_index = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __unicode__(self):
        return self.id

    def __repr__(self):
        return f'<novel_index_task {self.id}>'


class Picture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    origin_id = db.Column(db.String(255), default='UNKNOW')
    title = db.Column(db.String(255), default='UNKNOW')
    pidx = db.Column(db.String(255), default='0')
    size = db.Column(db.String(255), default='0 KB')
    author = db.Column(db.String(255), nullable=True)
    public_datetime = db.Column(db.DateTime, nullable=True)
    link = db.Column(db.String(255), nullable=True)
    task_id = db.Column(db.String(255), nullable=True)
    status = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now)
    deleted_at = db.Column(db.DateTime)

    def __unicode__(self):
        return self.title

    def __repr__(self):
        return f"<Picture {self.title}>"
