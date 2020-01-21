# -*- coding: UTF-8 -*-
# author: 'ACIOBANI'

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from microblog.configuration import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from views import routes, models
