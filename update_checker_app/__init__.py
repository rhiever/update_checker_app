#!/usr/bin/env python
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from .helpers import configure_logging

__version__ = '0.1'

DB_URI = 'postgresql://@/updatechecker'

APP = Flask(__name__)
APP.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

configure_logging(APP)
db = SQLAlchemy(APP)

from .controllers import *


def main():
    db.create_all()
    APP.run('', 65429, processes=4)
