from flask import Blueprint
from service.user_service import user_login_service, user_register_service, index, logout

user_page = Blueprint('user_page', __name__)

user_page.add_url_rule("/", methods=['GET','POST'], view_func=user_login_service)
user_page.add_url_rule("/login", methods=['GET','POST'], view_func=user_login_service)
user_page.add_url_rule("/register", methods=['GET','POST'], view_func=user_register_service)
user_page.add_url_rule("/index", view_func=index)
user_page.add_url_rule("/logout", view_func=logout)