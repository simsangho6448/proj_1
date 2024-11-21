from flask import Blueprint
from service.realtime_arriaval_service import realtime_arrival

# 블루프린트 생성
bp = Blueprint('realtime_arrival', __name__)

bp.add_url_rule("/api/realtimeArrival", methods=['GET'], view_func=realtime_arrival)