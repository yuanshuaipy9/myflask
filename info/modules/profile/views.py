from flask import render_template, g, redirect, request, jsonify, current_app

from info import constants
from info.modules.profile import profile_blu
from info.utils.common import user_login_data
from info.utils.image_storage import storage
from info.utils.response_code import RET

@profile_blu.route("/collection")
@user_login_data
def user_collection():
    user=g.user
    # 获取参数
    page=request.args.get("p",1)

    # 判断参数
    try:
        page=int(page)
    except Exception as e:
        current_app.logger.error(e)

    # 查询用户指定页数的收藏的新闻
    news_list=[]
    current_page=1
    total_page=1
    try:
        paginate=user.collection_news.paginate(page,constants.USER_COLLECTION_MAX_NEWS,False)
        current_page = paginate.page
        total_page = paginate.pages
        news_list=paginate.items
    except Exception as e:
        current_app.logger.error(e)

    news_dict_li=[]
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())

    data={
        "current_page":current_page,
        "total_page":total_page,
        "collections":news_dict_li
    }
    return render_template('news/user_collection.html', data=data)




@profile_blu.route("/pass_info",methods=["post","get"])
@user_login_data   # 用户必须登录才能进来
def pass_info():
    user=g.user
    if request.method=="GET":
        return render_template("news/user_pass_info.html",data={"user":user.to_dict()})

    # 1. 获取参数
    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")

    # 2. 校验参数
    if not all([old_password,new_password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 判断密码
    if not user.check_password(old_password):
        return jsonify(errno=RET.PWDERR, errmsg="原密码错误")

    #  设置新密码
    user.password = new_password

    return jsonify(errno=RET.OK, errmsg="保存成功")


@profile_blu.route("/pic_info",methods=["post","get"])
@user_login_data   # 用户必须登录才能进来
def pic_info():
    user=g.user
    if request.method=="GET":
        return render_template("news/user_pic_info.html",data={"user":user.to_dict()})

    #  如果是POST表示修改头像
    # 1. 取到上传的图片
    try:
        avatar=request.files.get("avatar").read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 上传头像
    try:
        # 使用自已封装的storage方法去进行图片上传
        key=storage(avatar)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传头像失败")

    user.avatar_url=key
    return jsonify(errno=RET.OK,errmsg="OK",data={"avatar_url":constants.QINIU_DOMIN_PREFIX+key})




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