import time
from datetime import datetime, timedelta

from flask import render_template, request, current_app, session, redirect, url_for, g

from info import constants
from info.models import User, News
from info.modules.admin import admin_blu
from info.utils.common import user_login_data


@admin_blu.route("/news_review")
def news_review():
    page=request.args.get("p",1)
    keywords=request.args.get("keywords",None)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    news = []
    current_page = 1
    total_page = 1

    filter=[News.status != 0]
    if keywords:
        filter.append(News.title.contains(keywords))
    try:
        paginate = News.query.filter(*filter).order_by(News.create_time.desc()).paginate(page,constants.ADMIN_NEWS_PAGE_MAX_COUNT,False)
        news = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    news_dict_li = []
    for a in news:
        news_dict_li.append(a.to_review_dict())

    context = {
        "total_page": total_page,
        "current_page": current_page,
        "news_list": news_dict_li
    }
    return render_template('admin/news_review.html', data=context)


@admin_blu.route("/user_list")
def user_list():
    page=request.args.get("p",1)

    try:
        page=int(page)
    except Exception as e:
        current_app.logger.error(e)
        page=1

    users=None
    current_page=1
    total_page=1
    try:
        paginate=User.query.filter(User.is_admin==False).paginate(page,constants.ADMIN_NEWS_PAGE_MAX_COUNT,False)
        users=paginate.items
        current_page=paginate.page
        total_page=paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    users_dict_li=[]
    for u in users:
        users_dict_li.append(u.to_admin_dict())

    data={
        "current_page":current_page,
        "total_page":total_page,
        "users":users_dict_li
    }
    return render_template("admin/user_list.html",data=data)

@admin_blu.route("/user_count")
def user_count():

    # 总人数
    total_count=0
    try:
        total_count=User.query.filter(User.is_admin==False).count()
    except Exception as e:
        current_app.logger.error(e)

    # 月新增人数
    mon_count=0
    t=time.localtime()
    begin_mon_date=datetime.strptime(("%d-%02d-01" % (t.tm_year,t.tm_mon)),"%Y-%m-%d")
    try:
        mon_count = User.query.filter(User.is_admin == False,User.create_time>begin_mon_date).count()
    except Exception as e:
        current_app.logger.error(e)
    # 日新增人数
    day_count = 0
    begin_day_date = datetime.strptime(('%d-%02d-%02d' % (t.tm_year, t.tm_mon, t.tm_mday)), "%Y-%m-%d")
    try:
        day_count = User.query.filter(User.is_admin == False, User.create_time > begin_day_date).count()
    except Exception as e:
        current_app.logger.error(e)

    # 折线图数据

    active_time = []
    active_count = []

    # 取到今天的时间字符串
    today_date_str = ("%d-%02d-%02d" % (t.tm_year, t.tm_mon, t.tm_mday))
    # 转成时间对象
    today_date = datetime.strptime(today_date_str, "%Y-%m-%d")

    for i in range(0,31):
        begin=today_date-timedelta(days=i)
        end=today_date-timedelta(days=(i-1))
        count=User.query.filter(User.is_admin==False,User.last_login>begin,User.last_login<end).count()
        active_count.append(count)
        active_time.append(begin.strftime("%Y-%m-%d"))

    # 让最近的一天显示在最后
    active_time.reverse()
    active_count.reverse()

    data={
        "total_count": total_count,
        "mon_count": mon_count,
        "day_count": day_count,
        "active_time": active_time,
        "active_count": active_count
    }
    return render_template('admin/user_count.html', data=data)


@admin_blu.route("/index")
@user_login_data
def index():
    user = g.user
    return render_template("admin/index.html",user=user.to_dict())


@admin_blu.route("/login",methods=["post","get"])
def login():
    if request.method=="GET":
        user_id = session.get("user_id", None)
        is_admin = session.get("is_admin", False)
        if user_id and is_admin:
            return redirect(url_for("admin.index"))
        return render_template("admin/login.html")

    # 取到登陆的参数
    username=request.form.get("username")
    password=request.form.get("password")

    # 判断参数
    if not all([username,password]):
        return render_template('admin/login.html', errmsg="参数错误")

    # 查询当前用户
    try:
        user=User.query.filter(User.mobile==username,User.is_admin==True).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/login.html', errmsg="用户信息查询失败")

    if not user:
        return render_template('admin/login.html', errmsg="未查询到用户信息")

    # 校验密码
    if not user.check_password(password):
        return render_template('admin/login.html', errmsg="用户名或者密码错误")

    session["user_id"] = user.id
    session["mobile"] = user.mobile
    session["nick_name"] = user.nick_name
    session["is_admin"] = user.is_admin

    # 跳转到后面管理首页
    return redirect(url_for("admin.index"))