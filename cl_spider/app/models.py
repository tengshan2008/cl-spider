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
    status = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now)
    deleted_at = db.Column(db.DateTime)

    def __unicode__(self):
        return self.title

    def __repr__(self):
        return f"<Novel {self.title}>"


class Picture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    origin_id = db.Column(db.String(255), default='UNKNOW')
    title = db.Column(db.String(255), default='UNKNOW')
    pidx = db.Column(db.String(255), default='0')
    size = db.Column(db.String(255), default='0 KB')
    author = db.Column(db.String(255), nullable=True)
    public_datetime = db.Column(db.DateTime, nullable=True)
    link = db.Column(db.String(255), nullable=True)
    status = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now)
    deleted_at = db.Column(db.DateTime)

    def __unicode__(self):
        return self.title

    def __repr__(self):
        return f"<Picture {self.title}>"
