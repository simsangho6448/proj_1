from flask import Flask
from flask_cors import CORS
# import pymysql  # 필요 CHECK
import logging
# from datetime import datetime  # 필요 CHECK

# 블루프린트 임포트
from route.search_station import bp as search_station_bp
from route.realtime_arrival import bp as realtime_arrival_bp
from route.user_route import user_page
from route.info_board import info_board
from route.deal_board import deal_board_page

# 로깅 설정
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)
app.secret_key = 'zl934h23i23I23lsc94b'

# 블루프린트 등록
app.register_blueprint(search_station_bp)
app.register_blueprint(realtime_arrival_bp)
app.register_blueprint(user_page)
app.register_blueprint(info_board)
app.register_blueprint(deal_board_page)


if __name__ == '__main__':
    app.run(debug=True)