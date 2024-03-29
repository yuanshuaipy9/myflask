from flask import render_template, g, redirect, request, jsonify, current_app

from info import constants, db
from info.models import Category, News
from info.modules.profile import profile_blu
from info.utils.common import user_login_data
from info.utils.image_storage import storage
from info.utils.response_code import RET

@profile_blu.route("/news_list")
@user_login_data
def news_list():
    user=g.user
    # 获取参数
    page=request.args.get("p",1)
    # 判断参数
    try:
        page=int(page)
    except Exception as e:
        current_app.logger.error(e)
        page=1

    user_news=[]
    current_page = 1
    total_page = 1
    try:
        paginate=News.query.filter(News.user_id==user.id).paginate(page,constants.USER_COLLECTION_MAX_NEWS, False)
        user_news = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    news_dict_li=[]
    for news in user_news:
        news_dict_li.append(news.to_review_dict())

    data={
        "news_list": news_dict_li,
        "total_page": total_page,
        "current_page": current_page,
    }
    return render_template("news/user_news_list.html",data=data)



@profile_blu.route("/news_release",methods=["GET","POST"])
@user_login_data
def news_release():
    if request.method == "GET":
        # 加载新闻分类数据
        categories = []
        try:
            categories=Category.query.all()
        except Exception as e:
            current_app.logger.error(e)

        category_dict_li=[]
        for category in categories:
            category_dict_li.append(category.to_dict())

        category_dict_li.pop(0)

        return render_template("news/user_news_release.html",data={"categories": category_dict_li})

    # 1. 获取要提交的数据
    # 标题
    title=request.form.get("title")
    # 新闻来源
    source="个人发布"
    # 摘要
    digest=request.form.get("digest")
    # 新闻内容
    content=request.form.get("content")
    # 索引图片
    index_image=request.files.get("index_image")
    # 分类id
    category_id=request.form.get("category_id")

    # 校验参数
    if not all([title, source, digest, content, index_image, category_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    try:
        category_id = int(category_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    # 3.取到图片，将图片上传到七牛云
    try:
        index_image_data=index_image.read()
        # 上传七牛云
        key=storage(index_image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    # 初始化模型
    news=News()
    news.title = title
    news.digest = digest
    news.source = source
    news.content = content
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
    news.category_id = category_id
    news.user_id = g.user.id
    # 1代表待审核状态
    news.status = 1

    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)

    return jsonify(errno=RET.OK, errmsg="OK")


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
        page = 1

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