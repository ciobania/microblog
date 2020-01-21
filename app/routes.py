# -*- coding: UTF-8 -*-
# author: 'ACIOBANI'
from datetime import datetime

from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required

from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm
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


@app.route('/profile/<user_name>')
@login_required
def user_profile(user_name):
    user = User.query.filter_by(user_name=user_name).first_or_404()
    posts = Post.query.filter_by(author=current_user or user).all()

    return render_template('user.html',
                           user=user,
                           posts=posts)


@app.route('edit_profile/', methods=['GET', 'POST'])
@login_required
def edit_profile():
    edit_profile_form = EditProfileForm()
    if edit_profile_form.validate_on_submit():
        current_user.user_name = edit_profile_form.user_name
        current_user.about_me = edit_profile_form.about_me
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        edit_profile_form.user_name.data = current_user.user_name
        edit_profile_form.about_me.data = current_user.about_me
        return render_template('edit_profile.html',
                               title='Edit Profile',
                               form=edit_profile_form)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
