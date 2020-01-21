# -*- coding: UTF-8 -*-
# author: 'ACIOBANI'
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required

from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User, Post
from app.routes_utils import get_next_page_or


@app.route('/')
@app.route('/index')
@login_required
def index():
    """
    App Homepage route
    """
    print('in index')
    posts = Post.query.filter_by(author=current_user).all()
    return render_template('index.html',
                           title='Home',
                           posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    App Login route to login a user.
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(user_name=login_form.user_name.data).first()
        if user and user.check_password(login_form.password.data):
            login_user(user, remember=login_form.remember_me.data)
            return redirect(get_next_page_or('index'))
        flash('Invalid username or password')

    return render_template('login.html',
                           title='real Sign in',
                           form=login_form)


@app.route('/logout')
def logout():
    """
    App Logout route to logout a user.
    """
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    register_form = RegistrationForm()
    if register_form.validate_on_submit():
        params = {'email': register_form.email.data,
                  'user_name': register_form.user_name.data}
        user = User(**params)
        user.set_password(register_form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('registration.html',
                           title='Register',
                           form=register_form)
