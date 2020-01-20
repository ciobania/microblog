# -*- coding: UTF-8 -*-
# author: 'ACIOBANI'
from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Adrian'}

    return render_template('index.html',
                           title='Home',
                           user=user)
