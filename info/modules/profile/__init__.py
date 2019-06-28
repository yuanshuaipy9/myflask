# 登陆注册的相关业务逻辑都放在当前模块
from flask import Blueprint

profile_blu=Blueprint("profile",__name__,url_prefix="/user")

from . import views
