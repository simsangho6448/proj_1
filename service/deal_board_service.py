from flask import *
import pymysql.cursors
from DBconn import *
import logging
from service.util_service import util_file_upload_service,util_comment_list_service
from datetime import datetime

def deal_board_list_service():
    station = request.args.get('station', None)
    cursor = dbconn.get_db().cursor(pymysql.cursors.DictCursor)
    sql=''
    try:
        if station:
        
            sql = '''
                SELECT 
                    DB.DEAL_BRD_NO,
                    DB.DEAL_BRD_TITL,
                    DB.DEAL_BRD_CTNT,
                    DB.DEAL_BRD_CATE,
                    DB.DEAL_BRD_PRICE,
                    DB.DEAL_BRD_IMG_NAME,
                    DB.DEAL_BRD_STATE,
                    DB.HIT,
                    DB.REGDT,
                    DB.REGID,
                    COUNT(BC.BRD_NO) AS CMNTCNT
                FROM DEAL_BOARD DB
                left outer join board_comment BC 
                    on DB.DEAL_BRD_NO = BC.BRD_NO
                where DB.DEL_FLAG = 'N' AND DB.DEAL_BRD_CATE = %s
                group by DB.DEAL_BRD_NO, BC.BRD_TYPE 
                having BC.BRD_TYPE != 'I' or BC.BRD_TYPE is NULL
                order by DB.DEAL_BRD_NO desc ;
            '''
            cursor.execute(sql,(station,))
        else:
            sql = '''
                SELECT 
                    DB.DEAL_BRD_NO,
                    DB.DEAL_BRD_TITL,
                    DB.DEAL_BRD_CTNT,
                    DB.DEAL_BRD_CATE,
                    DB.DEAL_BRD_PRICE,
                    DB.DEAL_BRD_IMG_NAME,
                    DB.DEAL_BRD_STATE,
                    DB.HIT,
                    DB.REGDT,
                    DB.REGID,
                    COUNT(BC.BRD_NO) AS CMNTCNT
                FROM DEAL_BOARD DB
                left outer join board_comment BC 
                    on DB.DEAL_BRD_NO = BC.BRD_NO
                where DB.DEL_FLAG = 'N' 
                group by DB.DEAL_BRD_NO, BC.BRD_TYPE 
                having BC.BRD_TYPE != 'I' or BC.BRD_TYPE is NULL
                order by DB.DEAL_BRD_NO desc ;
            '''
            cursor.execute(sql)
    
        result = cursor.fetchall()
        
    finally:
        dbconn.get_db().close()
    
    return render_template("/deal_board/deal_board.html",data=result,station=station)

def deal_board_detail_service():
    #--게시글 번호 가져와서 하나 선택
    DEAL_BRD_NO = request.args.get("DEAL_BRD_NO",0)
    station = request.args.get('station', None)
    try:
        sql = '''
            SELECT
                DB.DEAL_BRD_NO,
                DB.DEAL_BRD_TITL,
                DB.DEAL_BRD_CTNT,
                DB.DEAL_BRD_PRICE,
                DB.DEAL_BRD_IMG_NAME,
                DB.DEAL_BRD_STATE,
                DB.DEAL_BRD_CATE,
                DB.HIT,
                DB.REGDT,
                DB.REGID,
                COUNT(BC.BRD_NO) AS CMNTCNT
            from deal_board DB 
            left outer join board_comment BC 
                on DB.DEAL_BRD_NO = BC.BRD_NO
            WHERE DB.DEAL_BRD_NO = {0}
            group by DB.DEAL_BRD_NO, BC.BRD_TYPE 
            having BC.BRD_TYPE != 'I' or BC.BRD_TYPE is NULL ;
        '''.format(DEAL_BRD_NO)
        print(sql)
        cursor = dbconn.get_db().cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql)
        result = cursor.fetchone()
        #--조회수 +1
        sql = '''
            UPDATE deal_board set HIT = HIT +1 WHERE DEAL_BRD_NO = {0}
        '''.format(DEAL_BRD_NO)
        print(sql)
        cursor.execute(sql)
        
    except Exception as e:
        flash(f"오류 발생: {str(e)}")
        return render_template('/deal_board/deal_board.html')
    finally:
        dbconn.get_db().close()
        
    cm_data = util_comment_list_service(DEAL_BRD_NO,'D')
    
    return render_template("/deal_board/deal_board_detail.html",data=result,station=station,cm_data=cm_data)
    
def deal_board_reg_service():
    if request.method == 'GET':
        station = request.args.get('station', None)
        return render_template("/deal_board/deal_board_reg.html", station=station)
    elif request.method == 'POST':
        station = request.form.get("station")
        DEAL_BRD_TITL = request.form.get('DEAL_BRD_TITL')
        DEAL_BRD_PRICE = request.form.get('DEAL_BRD_PRICE')
        DEAL_BRD_CTNT = request.form.get('DEAL_BRD_CTNT')
        
        # if not all([DEAL_BRD_TITL, DEAL_BRD_PRICE, DEAL_BRD_CTNT]):
        #     flash("제목, 가격, 내용을 입력하세요.")
        #     # return render_template("/deal_board/deal_reg.html",station=station)
        #     return redirect(url_for('deal_board_page.deal_board_reg_service',station=station))
            
        file = request.files['DEAL_BRD_IMG_NAME']
        DEAL_BRD_IMG_NAME = util_file_upload_service(file)
        # if DEAL_BRD_IMG_NAME == 0:
        #     flash("지원하지 않는 확장자 또는 파일입니다.")
        #     # return render_template("/deal_board/deal_reg.html",station=station) 
        #     return redirect(url_for('deal_board_page.deal_board_reg_service',station=station))
        
        try:
            cursor = dbconn.get_db().cursor(pymysql.cursors.DictCursor)
            sql = '''
                INSERT INTO deal_board
                    (DEAL_BRD_TITL, DEAL_BRD_CTNT, DEAL_BRD_CATE, DEAL_BRD_PRICE, DEAL_BRD_IMG_NAME, REGID)
                VALUES(%s, %s, %s, %s, %s, %s);
                '''
            print(sql)
            print(DEAL_BRD_TITL,DEAL_BRD_CTNT,station,DEAL_BRD_PRICE,DEAL_BRD_IMG_NAME,session['user_id'])
            cursor.execute(sql,(DEAL_BRD_TITL,DEAL_BRD_CTNT,station,DEAL_BRD_PRICE,DEAL_BRD_IMG_NAME,session['user_id']))
            
        except Exception as e:
            flash(f"오류가 발생했습니다! 다시 시도해주세요.")
            # return render_template("/deal_board/deal_board_reg.html",station=station)
            logging.error(f'Error during registration for user: {str(e)}')
            return redirect(url_for('deal_board_page.deal_board_reg_service',station=station))
        finally:
            dbconn.get_db().close()
        
        flash(f"작성 완료되었습니다.")
        # return render_template("/deal_board/deal_board.html",station=station)
        return redirect(url_for('deal_board_page.deal_board_list_service',station=station))
        
def deal_board_upd_service():
    
    if request.method == 'GET':
        station = request.args.get('station', None)
        DEAL_BRD_NO = request.args.get('DEAL_BRD_NO', None)
        
        try:
            sql = '''
                SELECT
                    DB.DEAL_BRD_NO,
                    DB.DEAL_BRD_TITL,
                    DB.DEAL_BRD_CTNT,
                    DB.DEAL_BRD_PRICE,
                    DB.DEAL_BRD_IMG_NAME,
                    DB.DEAL_BRD_STATE,
                    DB.DEAL_BRD_CATE,
                    DB.HIT,
                    DB.REGDT,
                    DB.REGID,
                    COUNT(BC.BRD_NO) AS CMNTCNT
                from deal_board DB 
                left outer join board_comment BC 
                    on DB.DEAL_BRD_NO = BC.BRD_NO
                WHERE DB.DEAL_BRD_NO = {0}
                group by DB.DEAL_BRD_NO, BC.BRD_TYPE 
                having BC.BRD_TYPE != 'I' or BC.BRD_TYPE is NULL ;
            '''.format(DEAL_BRD_NO)
            cursor = dbconn.get_db().cursor(pymysql.cursors.DictCursor)
            cursor.execute(sql)
            result = cursor.fetchone()
        
        except Exception as e:
            flash(f"오류 발생: {str(e)}")
            return render_template('/deal_board/deal_board.html')
        finally:
            dbconn.get_db().close()
    
        return render_template("/deal_board/deal_board_upd.html",data=result,station=station)
        
    if request.method == 'POST':
        station = request.form.get("station")
        DEAL_BRD_NO = request.form.get('DEAL_BRD_NO')
        DEAL_BRD_TITL = request.form.get('DEAL_BRD_TITL')
        DEAL_BRD_PRICE = request.form.get('DEAL_BRD_PRICE')
        DEAL_BRD_CTNT = request.form.get('DEAL_BRD_CTNT')
        old_file = request.form.get('old_file')
        
        file = request.files['DEAL_BRD_IMG_NAME']
        DEAL_BRD_IMG_NAME = util_file_upload_service(file)
        
        if DEAL_BRD_IMG_NAME == 0 :
            DEAL_BRD_IMG_NAME = old_file
        
        try:
            cursor = dbconn.get_db().cursor(pymysql.cursors.DictCursor)
            sql = '''
                UPDATE deal_board set
                    DEAL_BRD_TITL = %s, 
                    DEAL_BRD_CTNT = %s,
                    DEAL_BRD_PRICE = %s,
                    DEAL_BRD_IMG_NAME = %s,
                    UPDID = %s,
                    UPDDT = %s
                WHERE DEAL_BRD_NO = %s
                '''
            cursor.execute(sql,(DEAL_BRD_TITL,DEAL_BRD_CTNT,DEAL_BRD_PRICE,DEAL_BRD_IMG_NAME,session['user_id'], datetime.now(),DEAL_BRD_NO))
            
        except Exception as e:
            flash(f"오류가 발생했습니다! 다시 시도해주세요.")
            return redirect(url_for('deal_board_page.deal_board_upd_service',DEAL_BRD_NO=DEAL_BRD_NO,station=station))
        finally:
            dbconn.get_db().close()
        
        flash(f"수정 완료되었습니다.")
    
    return redirect(url_for('deal_board_page.deal_board_list_service',station=station))

def deal_board_del_service():
    
    station = request.args.get("station")
    DEAL_BRD_NO = request.args.get('DEAL_BRD_NO')
    try:
            sql = '''
                UPDATE deal_board
                SET DEL_FLAG = 'Y', DELDT = %s
                WHERE DEAL_BRD_NO = %s
            '''
            cursor = dbconn.get_db().cursor(pymysql.cursors.DictCursor)
            cursor.execute(sql, (datetime.now(), DEAL_BRD_NO))
        
    except Exception as e:
        flash(f"오류 발생: {str(e)}")   
        return redirect(url_for('deal_board_page.deal_board_detail_service',DEAL_BRD_NO=DEAL_BRD_NO,station=station))
    finally:
        dbconn.get_db().close()
    
    flash(f"삭제가 완료되었습니다.")
    return redirect(url_for('deal_board_page.deal_board_list_service',station=station))
        
def board_comment_reg_service():
    
    station=request.form.get('station')
    BRD_CMNT_CTNT = request.form.get('BRD_CMNT_CTNT')
    BRD_TYPE = request.form.get('BRD_TYPE')
    BRD_NO = request.form.get('BRD_NO')
    
    try:
        cursor = dbconn.get_db().cursor(pymysql.cursors.DictCursor)
        sql = '''
            INSERT INTO board_comment
                (BRD_TYPE, BRD_NO, BRD_CMNT_CTNT, REGID)
            VALUES(%s, %s, %s, %s);
            '''
        cursor.execute(sql,(BRD_TYPE,BRD_NO,BRD_CMNT_CTNT,session['user_id']))
        
    except Exception as e:
        flash(f"오류가 발생했습니다! 다시 시도해주세요.")
        return redirect(url_for('deal_board_page.deal_board_detail_service',DEAL_BRD_NO=BRD_NO,station=station))
    finally:
        dbconn.get_db().close()
    
    flash(f"작성 완료되었습니다.")
    return redirect(url_for('deal_board_page.deal_board_detail_service',DEAL_BRD_NO=BRD_NO,station=station))

def board_comment_del_service():
    
    station=request.args.get('station')
    BRD_CMNT_NO = request.args.get('BRD_CMNT_NO')
    BRD_NO = request.args.get('DEAL_BRD_NO')
    
    try:
        cursor = dbconn.get_db().cursor(pymysql.cursors.DictCursor)
        sql = '''
            UPDATE board_comment SET
                DELDT = %s, DEL_FLAG = %s
            WHERE BRD_CMNT_NO = %s'''
        cursor.execute(sql,(datetime.now(),'Y',BRD_CMNT_NO))
    
    except Exception as e:
        flash(f"오류가 발생했습니다! 다시 시도해주세요.")
        return redirect(url_for('deal_board_page.deal_board_detail_service',DEAL_BRD_NO=BRD_NO,station=station))
    finally:
        dbconn.get_db().close()
    
    flash(f"삭제 완료되었습니다.")
    return redirect(url_for('deal_board_page.deal_board_detail_service',DEAL_BRD_NO=BRD_NO,station=station))