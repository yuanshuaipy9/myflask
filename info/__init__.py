from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_session import Session
from flask.ext.wtf import CSRFProtect
from redis import StrictRedis

from config import config

# 初始化数据库
# 在Flask很多扩展里面都可以先初始化扩展的对象，然后再去调用init_app方法去初始化
db=SQLAlchemy()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    redis_store=StrictRedis(host=config[config_name].REDIS_HOST,port=config[config_name].REDIS_PORT)

    CSRFProtect(app)
    # 设置session保存指定位置
    Session(app)
    return app