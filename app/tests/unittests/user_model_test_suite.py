# -*- coding: UTF-8 -*-
# author: 'ACIOBANI'
import contextlib
import unittest
from datetime import timedelta, datetime

from sqlalchemy import create_engine, exc


from app import app, db
from app.models import User, Post


class UserModelTestSuite(unittest.TestCase):
    DB_NAME = ''

    @classmethod
    def setUpClass(cls):
        cls.DB_NAME = 'microblog_test'
        cls.DB_URI = f'postgresql://localhost/{cls.DB_NAME}'
        app.config['SQLALCHEMY_DATABASE_URI'] = cls.DB_URI
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        cls.create_db(cls.DB_NAME)

    @classmethod
    def tearDownClass(cls):
        cls.close_db_connections()
        cls.drop_db(cls.DB_NAME)

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(user_name='susan12', email='susan12@example.com')  # noqa
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))
        self.assertTrue(True)

    def test_avatar(self):
        u = User(user_name='john13', email='john13@example.com')  # noqa
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         'cf693a3f375a35ed152b865059e028d1'
                                         '?d=identicon&s=128'))

    def test_follow(self):
        u1 = User(user_name='john13', email='john13@example.com')  # noqa
        u2 = User(user_name='susan13', email='susan13@example.com')  # noqa
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u1.followers.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().user_name, 'susan13')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().user_name, 'john13')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def test_follow_posts(self):
        # create four users
        u1 = User(user_name='john1', email='john1@example.com')  # noqa
        u2 = User(user_name='susan1', email='susan1@example.com')  # noqa
        u3 = User(user_name='mary1', email='mary1@example.com')  # noqa
        u4 = User(user_name='david1', email='david1@example.com')  # noqa
        db.session.add_all([u1, u2, u3, u4])

        # create four posts
        now = datetime.utcnow()
        p1 = Post(body="post from john", author=u1,
                  created_at=now + timedelta(seconds=1))
        p2 = Post(body="post from susan", author=u2,
                  created_at=now + timedelta(seconds=4))
        p3 = Post(body="post from mary", author=u3,
                  created_at=now + timedelta(seconds=3))
        p4 = Post(body="post from david", author=u4,
                  created_at=now + timedelta(seconds=2))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # setup the followers
        u1.follow(u2)  # john follows susan
        u1.follow(u4)  # john follows david
        u2.follow(u3)  # susan follows mary
        u3.follow(u4)  # mary follows david
        db.session.commit()

        # check the followed posts of each user
        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])

    @classmethod
    def create_db(cls, db_name):
        cls.__execute_in_db('create', db_name)

    @classmethod
    def drop_db(cls, db_name):
        cls.__execute_in_db('drop', db_name)

    @classmethod
    def __execute_in_db(cls, action, db_name):
        db_query = f'{action} DATABASE {db_name}'
        cls.__execute(query=db_query)

    @classmethod
    def __execute(cls, query):
        with contextlib.suppress(exc.ProgrammingError):
            with create_engine('postgresql:///postgres',
                               isolation_level='AUTOCOMMIT').connect() \
                    as connection:
                connection.execute(query)
                connection.close()

    @classmethod
    def close_db_connections(cls):
        close_db_connections_query = f"""
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '{cls.DB_NAME}'
          AND pid <> pg_backend_pid();"""
        cls.__execute(close_db_connections_query)


if __name__ == '__main__':
    unittest.main(verbosity=2)
