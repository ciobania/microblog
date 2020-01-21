# -*- coding: UTF-8 -*-
# author: 'ACIOBANI'
from datetime import datetime

from microblog.views import db
from sqlalchemy.dialects.postgresql import UUID


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(UUID(as_uuid=True),
                   unique=True,
                   nullable=False,
                   primary_key=True,
                   index=True)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime,
                           nullable=False,
                           default=datetime.utcnow,
                           onupdate=datetime.utcnow)


class User(BaseModel):
    __tablename__ = 'users'

    user_name = db.Column(db.String(32),
                          index=True)
    email = db.Column(db.String(120))
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return f'<User: {self.user_name}'


class Post(BaseModel):
    __tablename__ = 'posts'

    body = db.Column(db.String(1024))
    title = db.Column(db.String(64))
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))


    def __repr__(self):
        return f'<Post: {self.title}'