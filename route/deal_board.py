from flask import Blueprint
from service.deal_board_service import deal_board_del_service, deal_board_detail_service, deal_board_list_service, deal_board_reg_service, deal_board_upd_service, board_comment_del_service, board_comment_reg_service

deal_board_page = Blueprint('deal_board_page', __name__, url_prefix='/deal_board')

deal_board_page.add_url_rule("/deal_board", methods=['GET','POST'], view_func=deal_board_list_service)
deal_board_page.add_url_rule("/detail", methods=['GET','POST'], view_func=deal_board_detail_service)
deal_board_page.add_url_rule("/reg", methods=['GET','POST'], view_func=deal_board_reg_service)
deal_board_page.add_url_rule("/upd", methods=['GET','POST'], view_func=deal_board_upd_service)
deal_board_page.add_url_rule("/del", methods=['GET','POST'], view_func=deal_board_del_service)
deal_board_page.add_url_rule("/comment_reg", methods=['GET','POST'], view_func=board_comment_reg_service)
deal_board_page.add_url_rule("/comment_del", methods=['GET','POST'], view_func=board_comment_del_service)