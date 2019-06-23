import random
import re
from datetime import datetime

from flask import request, abort, current_app, make_response, jsonify, session

from info import redis_store, constants, db
from info.libs.yuntongxun.sms import CCP
from info.models import User
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET
from . import passport_blu

@passport_blu.route("/logout")
def logout():
    session.pop('user_id', None)
    session.pop('mobile', None)
    session.pop('nick_name', None)

    return jsonify(errno=RET.OK, errmsg="退出成功")


@passport_blu.route("/login",methods=["post"])
def login():
    """
    1.接收参数
    2.校验参数
    3.
    :return:
    """
    params_dict = request.json
    mobile = params_dict.get("mobile")
    passport = params_dict.get("passport")

    if not all([mobile,passport]):
        return jsonify(errno=RET.DBERR, errmsg="参数有误")
    if not re.match("1[3456789]\d{9}", mobile):
        return jsonify(errno=RET.DBERR, errmsg="手机号码格式有误")
    # 校验密码
    try:
        user=User.query.filter(User.mobile==mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    if not user:
        return jsonify(errno=RET.NODATA, errmsg="用户不存在")

    if not user.check_password(passport):
        return jsonify(errno=RET.PWDERR, errmsg="用户名或者密码错误")

    session["user_id"] = user.id
    session["mobile"] = user.mobile
    session["nick_name"] = user.nick_name

    # 设置当前用户最后一次登录时间
    user.last_login=datetime.now()

    # 如果在视图函数中，对模型身上的属性有修改，那么需要commit到数据库保存
    # 但是其实可以不用自己去写，db.session.commit(),前提是对SQLAlchemy有过相关配置

    # try:
    #     db.session.commit()
    # except Exception as e:
    #     db.session.rollback()
    #     current_app.logger.error(e)

    # 5. 响应
    return jsonify(errno=RET.OK, errmsg="登录成功")



@passport_blu.route("/register",methods=["post"])
def register():
    """
    注册的逻辑
    1. 获取参数
    2. 校验参数
    3. 取到服务器保存的真实的短信验证码内容
    4. 校验用户输入的短信验证码内容和真实验证码内容是否一致
    5. 如果一致，初始化 User 模型，并且赋值属性
    6. 将 user 模型添加数据库
    7. 返回响应
    :return:
    """
    # 获取参数
    params_dict = request.json
    mobile = params_dict.get("mobile")
    sms_code = params_dict.get("smscode")
    password = params_dict.get("password")
    # 校验参数
    if not all([mobile, sms_code, password]):
        return jsonify(errno=RET.DBERR, errmsg="参数有误")
    if not re.match("1[3456789]\d{9}", mobile):
        return jsonify(errno=RET.DBERR, errmsg="手机号码格式有误")

    try:
        real_sms_code = redis_store.get("sms_"+mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")

    if not real_sms_code:
        return jsonify(errno=RET.NODATA, errmsg="验证码已过期")

    # 4. 校验用户输入的短信验证码内容和真实验证码内容是否一致
    if real_sms_code != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    # 5. 如果一致，初始化 User 模型，并且赋值属性
    user=User()
    user.mobile=mobile
    # 暂时没有昵称 ，使用手机号代替
    user.nick_name = mobile
    # 记录用户最后一次登录时间
    user.last_login = datetime.now()
    # 对密码做处理
    user.password=password

    # 6. 将 user 模型添加数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")

    # 往 session 中保存数据表示当前已经登录
    session["user_id"]=user.id
    session["mobile"]=user.mobile
    session["nick_name"]=user.nick_name

    # 7. 返回响应
    return jsonify(errno=RET.OK, errmsg="注册成功")

@passport_blu.route("/sma_code",methods=["post"])
def get_sms_code():
    """
    1.取到参数mobile，image_code，image_code_id
    2.判断是否有值
    3.取出redis里面存放的图片验证码
    4.与用户提交的验证码内容进行对比，如果对比不一致，返回 输入错误的验证码
    5.如果一致，生成验证码的内容（随机数据）
    6.发送短信验证码，并保存到redis中，设置过期时间
    7.告知发送结果
    :return:
    """
    params_dict=request.json
    mobile = params_dict.get("mobile")
    image_code = params_dict.get("image_code")
    image_code_id = params_dict.get("image_code_id")

    if not all([mobile,image_code,image_code_id]):
        return jsonify(errno=RET.DBERR,errmsg="参数有误")
    if not re.match("1[3456789]\d{9}",mobile):
        return jsonify(errno=RET.DBERR,errmsg="手机号码格式有误")

    try:
        real_image_code=redis_store.get("ImageCodeId_" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")

    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码已过期")
    if real_image_code.upper()!=image_code.upper():
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    sms_code_str="%06d" % random.randint(0,999999)
    current_app.logger.debug("短信验证码的内容是：%s" % sms_code_str)
    # result=CCP().send_template_sms(mobile,[sms_code_str,int(constants.SMS_CODE_REDIS_EXPIRES / 60)],1)
    # # 发送不成功
    # if result!=0:
    #     return jsonify(errno=RET.THIRDERR, errmsg="发送短信失败")
    # 发送成功 1.存储到redis以便后续验证    2.发送成功消息
    try:
        redis_store.set("sms_"+mobile,sms_code_str,constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")

    return jsonify(errno=RET.OK, errmsg="发送成功")



@passport_blu.route("/image_code")
def get_image_code():
    """
        生成图片验证码并返回
        1.取到参数
        2.判断参数是否有值
        3.生成图片验证码
        4.保存图片验证码文字内容到redis
        5.返回验证码图片
        :return:
        """
    # 1.取到参数
    # args:取到url中？后面的参数
    image_code_id = request.args.get("imageCodeId", None)
    # 2.判断参数是否有值
    if not image_code_id:
        return abort(403)
    # 3.生成图片验证码
    name, text, image = captcha.generate_captcha()
    # 4.保存图片验证码文字内容到redis
    try:
        redis_store.set("ImageCodeId_" + image_code_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)
    # 5.返回验证码图片
    response=make_response(image)
    response.headers["Content-Type"]="image/jpg"
    return response
