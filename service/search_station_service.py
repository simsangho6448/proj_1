from flask import render_template, jsonify, request
import logging, requests
import os

# 역 정보를 불러오는 함수
def fetch_station_data():
    try:
        api_key = os.getenv("SEOUL_API_KEY", "69796c6673686a7334304a564c5561") 
        response = requests.get(f'http://openapi.seoul.go.kr:8088/{api_key}/json/subwayStationMaster/1/788/')
        response.raise_for_status()
        
        data = response.json().get("subwayStationMaster", {}).get("row", [])
        line_9_stations = [station for station in data if station["ROUTE"] in ["9호선", "9호선(연장)"]]
        logging.info(f"Fetched line 9 station data: {line_9_stations}")
        return line_9_stations
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching station data: {e}")
        return []
    except ValueError:
        logging.error("Failed to parse JSON response.")
        return []
    
station_data = fetch_station_data()  # 역 데이터 로드

# 오류일 경우에만 JSOM응답 반환, 페이지 렌더링 엔드포인트
def search_station():
    requested_station_name = request.args.get('station_name', '').strip()
    logging.info(f"Requested Station: {requested_station_name}")

    # 요청된 역 이름으로 검색
    matching_stations = [
        {"name": station["BLDN_NM"], "latitude": station["LAT"], "longitude": station["LOT"]}
        for station in station_data if requested_station_name in station["BLDN_NM"]
    ]
    
    if matching_stations:
        logging.info(f"Matching Stations: {matching_stations}")
        return render_template('search_station.html', matching_stations=matching_stations) # 검색 페이지를 반환하여 템플릿을 렌더링
    else:
        logging.info("No matching station found.")
        return jsonify({"success": False, "message": "해당 이름의 역이 없습니다."})