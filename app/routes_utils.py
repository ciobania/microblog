# -*- coding: UTF-8 -*-
# author: 'ACIOBANI'
from flask import request, url_for, flash
from werkzeug.urls import url_parse

from app import db
from app.models import User


def get_next_page_or(default):
    next_page = request.args.get('next')
    if not isinstance(next_page, type(None)):
        if url_parse(next_page).netloc == "":
            return next_page
    return url_for(default)


def edit_follower_for_user(action, user_name, current_user):
    user = User.query.filter_by(user_name=user_name).first()
    if not user:
        flash(f"User '{user_name}' not found!")
        return url_for('index')
    if user == current_user:
        flash(f'You cannot {action} yourself!')
        return url_for('user', user_name=user_name)
    getattr(current_user, action)(user)
    db.session.commit()
    flash(f'You are following {user_name}!')
    return url_for('user', user_name=user_name)
