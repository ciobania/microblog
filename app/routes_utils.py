# -*- coding: UTF-8 -*-
# author: 'ACIOBANI'
from flask import request, url_for
from werkzeug.urls import url_parse


def get_next_page_or(default):
    next_page = request.args.get('next')
    if not isinstance(next_page, type(None)):
        if url_parse(next_page).netloc == "":
            return next_page
    return url_for(default)
