from flask import Blueprint
from service.search_station_service import search_station

bp = Blueprint('search_station', __name__, url_prefix='/search')

bp.add_url_rule('/search_station', methods=['GET'], view_func=search_station)