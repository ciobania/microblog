# -*- coding: UTF-8 -*-
# author: 'ACIOBANI'
from datetime import datetime

from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required

from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm
from app.models import User, Post
from app.routes_utils import get_next_page_or, edit_follower_for_user


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    """
    App Homepage route
    """
    post_form = PostForm()
    if post_form.validate_on_submit():
        new_post = Post(body=post_form.post.data, author=current_user)
        db.session.add(new_post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_page = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_page = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', next_page=next_page,
                           title='Home', prev_page=prev_page,
                           form=post_form,
                           posts=posts.items)


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


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    edit_profile_form = EditProfileForm(current_user.user_name)
    if edit_profile_form.validate_on_submit():
        current_user.user_name = edit_profile_form.user_name.data
        current_user.about_me = edit_profile_form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        edit_profile_form.user_name.data = current_user.user_name
        edit_profile_form.about_me.data = current_user.about_me
    return render_template('edit_profile.html',
                           title='Edit Profile',
                           form=edit_profile_form)


@app.route('/follow/<user_name>')
@login_required
def follow_user(user_name):
    params = {'action': 'follow',
              'user_name': user_name,
              'current_user': current_user}
    redirect_url_for = edit_follower_for_user(**params)
    return render_template(redirect_url_for)


@app.route('/unfollow/<user_name>')
@login_required
def unfollow_user(user_name):
    params = {'action': 'unfollow',
              user_name: user_name,
              current_user: current_user}
    redirect_url_for = edit_follower_for_user(**params)
    return render_template(redirect_url_for)


@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_page = url_for('index', page=posts.next_num) \
        if posts.has_next \
        else None
    prev_page = url_for('index', page=posts.prev_num) \
        if posts.has_prev \
        else None
    return render_template('index.html', next_page=next_page,
                           title='Explore', prev_page=prev_page,
                           posts=posts.items)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
