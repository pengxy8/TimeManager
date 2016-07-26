# -*- coding=utf-8 -*-
from flask import Flask
from flask.ext.login import LoginManager
from pymongo import MongoClient
from config import *

app=Flask(__name__)
app.config.from_object('config')

db=MongoClient(MONGO_HOST,MONGO_PORT).android

lm=LoginManager()
lm.init_app(app)
lm.login_view='login'

from api import user,activity
