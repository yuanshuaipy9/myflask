from flask import render_template, current_app, session, g, abort

from info.models import User, News
from info.utils.common import user_login_data
from . import news_blu


@news_blu.route("/<int:news_id>")
@user_login_data
def news_detail(news_id):
    user=g.user

    # 查询排行数据传递给后端
    news_list = []
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(6)
    except Exception as e:
        current_app.logger.error(e)

    news_dict_li = []
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())
    news=[]
    try:
        news=News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)

    if not news:
        # 报404错误，404错误统一显示页面后续再处理
        abort(404)
    # 更新新闻的点击次数
    news.clicks+=1

    data={
        "user": user.to_dict() if user else None,
        "news_dict_li": news_dict_li,
        "news":news
    }
    return render_template("news/detail.html",data=data)
