import logging

from redis import StrictRedis


class Config(object):
    """项目的配置"""


    SECRET_KEY="fMuNcrlM51xCLjytXYsTqxRoQPasbaGRNNomj8hTReQWlsis4zOtb3MJMADguL/Z"

    SQLALCHEMY_DATABASE_URI="mysql://root:mysql@127.0.0.1:3306/classflask"
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    # 在请求结束时，如果指定此配置为True，那么SQLAlchemy会自动执行一次db.session.commit
    SQLALCHEMY_COMMIT_ON_TEARDOWN=True

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

    # 设置日志等级
    LOG_LEVEL = logging.DEBUG



class DevelopmentConfig(Config):
    """开发环境下的配置"""
    DEBUG = True

class ProductionConfig(Config):
    """生产环境下的配置"""
    DEBUG = True
    LOG_LEVEL = logging.WARNING

class TestingConfig(Config):
    """单元测试环境下的配置"""
    DEBUG = True
    TESTING = True

config={"development":DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig
        }