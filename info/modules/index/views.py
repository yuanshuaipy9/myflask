from flask import render_template, current_app, session

from info.models import User
from . import index_blu

@index_blu.route("/")
def index():
    """
    显示首页
    1.如果用户已经登陆，将当前登陆用户的数据传到模板中，供模板显示
    :return:
    """
    user_id=session.get("user_id",None)
    user=None
    if user_id:
        # 尝试查询用户的模型
        try:
            user=User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    data={
        "user":user.to_dict() if user else None
    }

    return render_template("news/index.html",data=data)

@index_blu.route("/favicon.ico")
def favicon():
    return current_app.send_static_file("news/favicon.ico")