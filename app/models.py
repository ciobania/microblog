# -*- coding: UTF-8 -*-
# author: 'ACIOBANI'
import uuid
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager
from sqlalchemy.dialects.postgresql import UUID


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(UUID(as_uuid=True),
                   unique=True,
                   nullable=False,
                   primary_key=True,
                   index=True,
                   default=uuid.uuid4)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime,
                           nullable=False,
                           default=datetime.utcnow,
                           onupdate=datetime.utcnow)


class User(UserMixin, BaseModel):
    __tablename__ = 'users'

    user_name = db.Column(db.String(32),
                          index=True)
    email = db.Column(db.String(120))
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return f'<User: {self.user_name}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class Post(BaseModel):
    __tablename__ = 'posts'

    title = db.Column(db.String(64))
    body = db.Column(db.String(1024))
    user_id = db.Column(UUID(as_uuid=True),
                        db.ForeignKey('users.id'),
                        default=uuid.uuid4)

    def __repr__(self):
        return f'<Post: {self.title}>'
