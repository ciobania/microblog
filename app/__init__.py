# -*- coding: UTF-8 -*-
# author: 'ACIOBANI'
import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


app = Flask(__name__)
app.config.from_object(os.environ.get('APP_SETTINGS'))

db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from app import routes, models, errors

if not app.debug:
    SH_LOG_LEVEL = os.environ.get('SH_LOG_LEVEL', 'INFO')
    FH_LOG_LEVEL = os.environ.get('FH_LOG_LEVEL', 'DEBUG')
    LOGS_PATH = '{}/logs/'.format(os.path.dirname(__file__))
    if not os.path.exists(LOGS_PATH):
        os.makedirs(LOGS_PATH)
    LOG_FILE_NAME = '{}{}.log'.format(LOGS_PATH,
                                      'microblog.log')

    FH = RotatingFileHandler(LOG_FILE_NAME, maxBytes=10240, backupCount=10)
    FH.setLevel(getattr(logging, FH_LOG_LEVEL))
    # create console handler with a higher log level
    SH = logging.StreamHandler()
    SH.setLevel(getattr(logging, SH_LOG_LEVEL))

    # create formatter and add it to the handlers
    FORMATTER_PTTRN = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FORMATTER = logging.Formatter(FORMATTER_PTTRN)
    FH.setFormatter(LOG_FORMATTER)
    SH.setFormatter(LOG_FORMATTER)

    # add the handlers to the logger
    app.logger.addHandler(FH)
    app.logger.addHandler(SH)
    app.logger.setLevel(getattr(logging, FH_LOG_LEVEL))
    app.logger.info('Microblog startup')
