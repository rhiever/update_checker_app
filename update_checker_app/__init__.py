#!/usr/bin/env python
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from os import getenv

__version__ = '0.1'

DB_URI = 'postgresql://@/updatechecker'

APP = Flask(__name__)
APP.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
APP.debug = getenv('DEBUG')
db = SQLAlchemy(APP)

# Delay these imports until db is defined
from .controllers import *
from .helpers import configure_logging

configure_logging(APP)


def main():
    db.create_all()
    APP.run('', 65429, processes=4)
