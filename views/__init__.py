# -*- coding: UTF-8 -*-
# author: 'ACIOBANI'

from flask import Flask

app = Flask(__name__)

from app import routes
