from flask import jsonify, request
import logging
import requests

# 실시간 지하철 정보를 받아오는 함수
def fetch_realtime_arrival_data(station_name):
    """ 주어진 역 이름으로 서울시 API에서 실시간 지하철 정보를 가져옴 """
    api_url = f"http://swopenapi.seoul.go.kr/api/subway/6b586f764b686a733233766a617670/json/realtimeStationArrival/1/788/{station_name}"
    response = requests.get(api_url)

    if response.status_code == 200:
        return response.json()  # 성공 시 JSON 응답 반환
    else:
        logging.error(f"실시간 지하철 정보 요청 실패: {response.status_code}")
        return None
    
def get_realtime_arrival_with_fallback(station_name):
    """
    기본 역 이름으로 실시간 정보를 요청하되,
    실패 시 앞 두 글자를 이용해 다시 요청을 시도하는 예외 처리 포함
    """
    # 기본 이름으로 요청
    arrival_data = fetch_realtime_arrival_data(station_name)
    
    # 첫 요청 실패 시 앞 두 글자를 사용한 이름으로 재요청
    if not arrival_data or 'error' in arrival_data:
        short_station_name = station_name[:2]
        logging.info(f"기본 이름 '{station_name}'로 정보 가져오기 실패, '{short_station_name}'로 재시도 중")
        arrival_data = fetch_realtime_arrival_data(short_station_name)
    
    return arrival_data

# 실시간 도착 정보를 위한 라우트
def realtime_arrival():
    """
    클라이언트에서 전달된 역 이름으로 실시간 도착 정보를 제공하는 API 엔드포인트.
    """
    station_name = request.args.get('stationName')  # 클라이언트에서 전달된 역 이름
    if not station_name:
        return jsonify({"error": "역 이름이 필요합니다."}), 400

    # 실시간 도착 정보 요청 및 예외 처리
    arrival_data = get_realtime_arrival_with_fallback(station_name)
    
    # 성공적으로 데이터를 가져왔을 때와 실패 시의 응답 처리
    if arrival_data:
        return jsonify(arrival_data)
    else:
        return jsonify({"error": "실시간 정보를 가져오지 못했습니다."}), 500