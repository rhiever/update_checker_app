#!/usr/bin/env python
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

__version__ = '0.1'

DB_URI = 'sqlite:///database.db'

APP = Flask(__name__)
APP.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
db = SQLAlchemy(APP)

from .controllers import *


def main():
    db.create_all()
    APP.run('', 65429, processes=4)
