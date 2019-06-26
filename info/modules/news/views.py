from flask import render_template, current_app, session, g, abort, request, jsonify

from info import db
from info.models import User, News, Comment
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import news_blu

@news_blu.route("/news_comment",methods=["POST"])
@user_login_data
def comment_news():
    """
    评论新闻或者回复某条新闻下指定的评论
    :return:
    """
    user=g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    news_id=request.json.get("news_id")
    comment_content = request.json.get("comment")
    parent_id = request.json.get("parent_id")

    if not all([news_id,comment_content]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        news_id = int(news_id)
        if parent_id:
            parent_id = int(parent_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 3.初始化一个评论模型，并且赋值
    comment=Comment()
    comment.user_id = user.id
    comment.news_id = news_id
    comment.content = comment_content
    if parent_id:
        comment.parent_id=parent_id

    # 添加到数据库
    # 为什么要自己去commit()?，因为在return的时候需要用到 comment 的 id
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

    return jsonify(errno=RET.OK,errmsg="OK",data=comment.to_dict())

@news_blu.route("/news_collect",methods=["post"])
@user_login_data
def collect_news():
    """
    收藏新闻
    1.接收参数
    2.判断参数
    :return:
    """
    user=g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    news_id=request.json.get("news_id")
    action = request.json.get("action")

    if not all([news_id,action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if action not in ["collect", "cancel_collect"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        news_id=int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 查询新闻，并判断新闻是否存在
    try:
        news=News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    if not news:
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    # 4.收藏以及取消收藏
    if action=="cancel_collect":
        # 取消收藏
        if news in user.collection_news:
            user.collection_news.remove(news)
    else:
        # 收藏
        if news not in user.collection_news:
            user.collection_news.append(news)

    return jsonify(errno=RET.OK, errmsg="操作成功")

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

    is_collected = False

    # if 用户已登录：
    #     判断用户是否收藏当前新闻，如果收藏：
    #         is_collected = True
    if user:
        if news in user.collection_news:
            is_collected=True

    # 去查询评论数据
    comments=[]
    try:
        comments=Comment.query.filter(Comment.news_id==news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)

    comment_dict_li=[]
    for comment in comments:
        comment_dict_li.append(comment.to_dict())



    data={
        "user": user.to_dict() if user else None,
        "news_dict_li": news_dict_li,
        "news":news,
        "is_collected":is_collected,
        "comments":comment_dict_li
    }
    return render_template("news/detail.html",data=data)
