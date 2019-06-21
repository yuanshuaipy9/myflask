from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_session import Session
from flask.ext.wtf import CSRFProtect
from redis import StrictRedis

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db=SQLAlchemy(app)

redis_store=StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)

CSRFProtect(app)
# 设置session保存指定位置
Session(app)