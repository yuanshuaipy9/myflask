from flask import render_template, g, redirect, request

from info.modules.profile import profile_blu
from info.utils.common import user_login_data

@profile_blu.route("/base_info",methods=["post","get"])
@user_login_data   # 用户必须登录才能进来
def base_info():
    if request.method=="GET":
        return render_template("news/user_base_info.html",data={"user":g.user.to_dict()})


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