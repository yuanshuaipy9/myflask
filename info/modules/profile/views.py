from flask import render_template, g, redirect, request, jsonify

from info.modules.profile import profile_blu
from info.utils.common import user_login_data
from info.utils.response_code import RET


@profile_blu.route("/pic_info",methods=["post","get"])
@user_login_data   # 用户必须登录才能进来
def pic_info():
    user=g.user
    if request.method=="GET":
        return render_template("news/user_pic_info.html",data={"user":user.to_dict()})


@profile_blu.route("/base_info",methods=["post","get"])
@user_login_data   # 用户必须登录才能进来
def base_info():
    user=g.user
    if request.method=="GET":
        return render_template("news/user_base_info.html",data={"user":user.to_dict()})

    # 代表是修改用户数据
    # 1.取数据
    nick_name = request.json.get("nick_name")
    signature = request.json.get("signature")
    gender = request.json.get("gender")

    # 2.校验参数
    if not all([nick_name, signature, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    if gender not in ("WOMAN", "MAN"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    user.nick_name = nick_name
    user.signature = signature
    user.gender = gender

    return jsonify(errno=RET.OK, errmsg="OK")

@profile_blu.route("/info")
@user_login_data
def user_info():
    user=g.user
    if not user:
        return redirect("/")
    data={
        "user":user.to_dict()
    }
    return render_template("news/user.html",data=data)