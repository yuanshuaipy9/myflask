from flask import Flask, session
from flask.ext.sqlalchemy import SQLAlchemy   # 配置建议手打，不是从flask_sqlalchemy导入
from flask.ext.wtf import CSRFProtect    # 配置建议手打，不是从flask_wtf导入
from flask_script import Manager
from redis import StrictRedis
#可以指定session保存的位置
from flask_session import Session


class Config(object):
    DEBUG=True

    SECRET_KEY="fMuNcrlM51xCLjytXYsTqxRoQPasbaGRNNomj8hTReQWlsis4zOtb3MJMADguL/Z"

    SQLALCHEMY_DATABASE_URI="mysql://root:mysql@127.0.0.1:3306/classflask"
    SQLALCHEMY_TRACK_MODIFICATIONS=False

    # redis配置
    REDIS_HOST="127.0.0.1"
    REDIS_PORT=6379

    #Session保存配置
    SESSION_TYPE="redis"
    # 开启session签名
    SESSION_USE_SIGNER = True
    # 指定 Session 保存的 redis
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 设置需要过期
    SESSION_PERMANENT = False
    # 设置过期时间
    PERMANENT_SESSION_LIFETIME = 86400 * 2



app = Flask(__name__)
app.config.from_object(Config)
db=SQLAlchemy(app)

redis_store=StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)

CSRFProtect(app)
# 设置session保存指定位置
Session(app)

manager=Manager(app)



@app.route("/")
def index():
    session["aaa"]="itheima"
    return "index"


if __name__ == '__main__':
    app.run()


