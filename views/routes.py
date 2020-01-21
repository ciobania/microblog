# -*- coding: UTF-8 -*-
# author: 'ACIOBANI'
from flask import render_template, flash, redirect, url_for

from views import app
from views.forms import LoginForm


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Adrian'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]

    return render_template('index.html',
                           title='Home',
                           user=user,
                           posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        flash_msg = 'Login requested for user {}, remember_me={}'
        flash(flash_msg.format(login_form.username.data,
                               login_form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign in',
                           form=login_form)
