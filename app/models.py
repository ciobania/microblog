# -*- coding: UTF-8 -*-
# author: 'ACIOBANI'
import uuid
from datetime import datetime
from hashlib import md5

from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


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


followers = db.Table('followers',
                     db.Column('follower_id',
                               UUID(as_uuid=True),
                               db.ForeignKey('users.id')),
                     db.Column('followed_id',
                               UUID(as_uuid=True),
                               db.ForeignKey('users.id')))


class User(UserMixin, BaseModel):
    __tablename__ = 'users'

    user_name = db.Column(db.String(32),
                          index=True,
                          unique=True)
    email = db.Column(db.String(120),
                      index=True,
                      unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship(
        'User',
        secondary=followers,
        primaryjoin=lambda: followers.c.follower_id == User.id,
        secondaryjoin=lambda: followers.c.followed_id == User.id,
        backref=db.backref('followers',
                           lazy='dynamic'),
        lazy='dynamic')

    def __repr__(self):
        return f'<User: {self.user_name}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        gravatar_url = 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'
        return gravatar_url.format(digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def un_follow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        followed_filter = followers.c.followed_id == user.id
        return self.followed.filter(followed_filter).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.created_at.desc())


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

# ToDo: review this path of self-referential mapping
# class Followers(db.Model):
#     __table__name = 'followers'
#
#     followed_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
#     follower_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
