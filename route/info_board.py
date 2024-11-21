from flask import Blueprint
from service.info_board_service import info_board_list, create_post, view_post, edit_post, delete_post

info_board = Blueprint('info_board', __name__, url_prefix='/board')

info_board.add_url_rule('/', methods=['GET'], view_func=info_board_list)
info_board.add_url_rule('/create_post', methods=['GET', 'POST'],view_func=create_post)
info_board.add_url_rule('/post/<int:post_id>',view_func=view_post)
info_board.add_url_rule('/edit_post/<int:post_id>', methods=['GET', 'POST'],view_func=edit_post)
info_board.add_url_rule('/delete_post/<int:post_id>', methods=['GET'],view_func=delete_post)