from flask import render_template, request, current_app, session, redirect, url_for

from info.models import User
from info.modules.admin import admin_blu

@admin_blu.route("/index")
def index():
    return render_template("admin/index.html")

@admin_blu.route("/login",methods=["post","get"])
def login():
    if request.method=="GET":
        user_id = session["user_id"]
        is_admin = session["is_admin"]
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