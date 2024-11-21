from flask import render_template, request, redirect, url_for, session
from datetime import datetime

import pymysql.cursors
from DBconn import dbconn  # Import the database connection class
import pymysql

# 게시물 목록 표시
def info_board_list():
    # 데이터베이스 연결
    connection = dbconn.get_db()
    posts = []
    
    try:
        station = request.args.get('station')
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        # info_board 테이블로 수정
        sql = """
            SELECT INFO_BRD_NO, INFO_BRD_TITLE, INFO_BRD_CTNT, INFO_BRD_HIT, INFO_BRD_updated_at, REGID 
            FROM info_board 
            WHERE INFO_BRD_is_deleted = 'n' and INFO_BRD_CATE = %s
            ORDER BY INFO_BRD_updated_at DESC
        """
        cursor.execute(sql, (station, ))
        posts = cursor.fetchall()
    finally:
        connection.close()
    user_id = session.get('user_id')
    # info_board.html로 데이터 전달 시 info_board 변수로 전달       
    return render_template('info_board.html', info_board=posts, station=station, user_id=user_id)


# 글 작성 페이지 렌더링
def create_post():
    if request.method == 'GET':
        station = request.args.get('station')
        return  render_template('create_post.html',station=station)
    if request.method == 'POST':
        station = request.form['station']
        INFO_BRD_TITLE = request.form['INFO_BRD_TITLE']
        INFO_BRD_CTNT = request.form['INFO_BRD_CTNT']
        REGID = session.get('user_id')
        
        
        # MySQL에 연결하고 데이터 삽입
        connection = dbconn.get_db()
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO info_board (INFO_BRD_TITLE, INFO_BRD_CTNT, REGID,INFO_BRD_CATE) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (INFO_BRD_TITLE, INFO_BRD_CTNT, REGID, station))
            connection.commit()
        finally:
            connection.close()
        
        # 작성 완료 후 게시판으로 리디렉션
        return redirect(url_for('info_board.info_board_list',station=station))

# post_id를 가진 게시물을 DB에서 조회
def view_post(post_id):
    
    station = request.args.get('station')
    
    # 데이터베이스 연결
    connection = dbconn.get_db()
    cursor = connection.cursor()
    try:
        # 조회수 증가 쿼리 실행
        update_sql = "UPDATE info_board SET INFO_BRD_HIT = INFO_BRD_HIT + 1 WHERE INFO_BRD_NO = %s"
        cursor.execute(update_sql, (post_id,))
        
        # 해당 게시글 데이터 가져오기
        select_sql = """
            SELECT INFO_BRD_NO, INFO_BRD_TITLE, INFO_BRD_CTNT, REGID, INFO_BRD_HIT, INFO_BRD_created_at, INFO_BRD_updated_at,INFO_BRD_CATE
            FROM info_board 
            WHERE INFO_BRD_NO = %s
        """
        cursor.execute(select_sql, (post_id,))
        post = cursor.fetchone()
    finally:
        connection.close()
    
    # if post is None:
    #     return "Post not found", 404
    
    # return render_template('/post_detail.html', post=post, station=station)

# 게시물 수정 뷰 함수 / 편집페이지 접근 -> 수정 -> DB 반영 -> 페이지 로드
def edit_post(post_id):
    connection = dbconn.get_db()
    cursor = connection.cursor()
    if request.method == 'GET':
        station = request.args.get('station')
            
        # 해당 게시글 데이터 가져오기
        select_sql = """
            SELECT INFO_BRD_NO, INFO_BRD_TITLE, INFO_BRD_CTNT, REGID,INFO_BRD_CATE
            FROM info_board 
            WHERE INFO_BRD_NO = %s
        """
        cursor.execute(select_sql, (post_id,))
        post = cursor.fetchone()
        return render_template('edit_post.html',post=post,station=station)
    if request.method == 'POST':
        # 폼에서 전송된 데이터 가져오기
        station = request.form['station']
        INFO_BRD_TITLE = request.form['INFO_BRD_TITLE']
        INFO_BRD_CTNT = request.form['INFO_BRD_CTNT']
        
        # 데이터베이스에 수정 반영
        try:
            sql = """
                UPDATE info_board 
                SET INFO_BRD_TITLE = %s, INFO_BRD_CTNT = %s, INFO_BRD_updated_at = %s 
                WHERE INFO_BRD_NO = %s
            """
            cursor.execute(sql, (INFO_BRD_TITLE, INFO_BRD_CTNT, datetime.now(), post_id))
        finally:
            connection.close()
        
        # 수정 완료 후 게시판 페이지로 리디렉션
        return redirect(url_for('info_board.info_board_list', station=station))

    # else:
    #     # GET 요청 시 기존 데이터 가져오기
    #     post = get_post_by_id(post_id)
    #     if post is None:
    #         return "Post not found", 404
    #     return render_template('edit_post.html', post=post,station=station)

# 게시물을 삭제된 상태로 표시하는 함수    
def delete_post(post_id):
    station = request.args.get('station')
    
    # 데이터베이스 연결
    connection = dbconn.get_db()
    try:
        with connection.cursor() as cursor:
            # 삭제 상태를 업데이트하고 삭제 시간을 설정
            sql = """
                UPDATE info_board 
                SET INFO_BRD_is_deleted = 'y', INFO_BRD_deleted_at = %s 
                WHERE INFO_BRD_NO = %s
            """
            cursor.execute(sql, (datetime.now(), post_id))
        connection.commit()
    finally:
        connection.close()
    
    # 삭제 후 게시판 페이지로 리디렉션
    return redirect(url_for('info_board.info_board_list',station=station))

# # 해당 게시글 정보를 DB에서 조회
# def get_post_by_id(post_id):
#     # 데이터베이스 연결
#     connection = dbconn.get_db()
#     post = None
#     try:
#         with connection.cursor() as cursor:
#             sql = """
#                 SELECT INFO_BRD_NO, INFO_BRD_TITLE, INFO_BRD_CTNT, INFO_BRD_HIT, INFO_BRD_updated_at 
#                 FROM info_board 
#                 WHERE INFO_BRD_NO = %s
#             """
#             cursor.execute(sql, (post_id,))
#             post = cursor.fetchone()
#     finally:
#         connection.close()
#     return post

# 특정 지하철역 게시물을 표시하는 라우트
def station_posts(station_name):
    # get_posts_by_station 함수를 사용하여 해당 역 게시물 조회
    posts = info_board_list(station_name)
    return render_template('info_board.html', station_name=station_name, info_board=posts)
