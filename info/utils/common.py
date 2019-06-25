import functools
# 共用的自定义工具类
from flask import session, current_app, g

from info.models import User


def do_index_class(index):
    if index == 1:
        return "first"
    elif index == 2:
        return "second"
    elif index == 3:
        return "third"

    return ""


def user_login_data(f):
    # 使用functools.wraps去装饰内层函数，可以保持当前装饰器去装饰的函数的__name__的值不变
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id", None)
        user = None
        if user_id:
            # 尝试查询用户的模型
            try:
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)
        g.user = user
        return f(*args, **kwargs)

    return wrapper
