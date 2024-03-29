# -*- coding: UTF-8 -*-
# author: 'ACIOBANI'

from app import app, db
from app.models import User, Post

@app.shell_context_processor
def make_shell_context():
    return {'db':db, 'user': User, 'post': Post}
