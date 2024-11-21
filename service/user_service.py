from flask import *
import pymysql
from DBconn import *
from werkzeug.security import check_password_hash, generate_password_hash
import re
import logging
from service.search_station_service import fetch_station_data

# user.log 파일에 별도로 발생하는 log 저장
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

def user_login_service():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        id = request.form.get('id')
        pw = request.form.get('password')
        
        logging.info(f'Login attempt for user: {id}')
        cursor = dbconn.get_db().cursor(pymysql.cursors.DictCursor)
        SQL = "SELECT * FROM member WHERE MEMB_ID = %s"
        try:
            cursor.execute(SQL, (id,))
            user = cursor.fetchone()
            # 조회 결과 하나 이상이고 비밀번호가 일치하는 경우
            if user and check_password_hash(user['MEMB_PSWD'], pw):
                # 로그인 성공 시 세션에 사용자 정보 저장
                session['user_id'] = user['MEMB_ID']
                session['user_name'] = user['MEMB_NAME']
                flash("로그인 성공!")
                logging.info(f'Successful login for user: {id}')
                return redirect(url_for('user_page.index')) #경로수정
            # 조회 결과 없거나 비밀번호가 일치하지 않은 경우
            else:
                flash("로그인 실패. 아이디 또는 비밀번호를 확인해주세요.")
                logging.warning(f'Failed login attempt for user: {id}')
                return render_template('login.html')
        except Exception as e:
            flash(f"오류 발생: {str(e)}")
            logging.error(f'Error during login for user {id}: {str(e)}')
            return render_template('login.html')
        finally:
            dbconn.get_db().close()

def user_register_service():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        id = request.form.get('id')
        name = request.form.get('name')
        pw = request.form.get('pw')
        cpw = request.form.get('pwcon')
        
        # 회원가입 시도
        logging.info(f'Registartion attempt for user: {id}, {name}')

        # 필수 입력 사항 모두 입력하지 않은 경우
        if not all([id, name, pw, cpw]):
            flash("모든 필드를 입력해주세요.")
            return render_template('register.html')

        # 비밀번호와 비밀번호 확인이 같지 않은 경우
        if pw != cpw:
            flash("비밀번호가 일치하지 않습니다.")
            return render_template('register.html')

        # 비밀번호 정책(최소 8자 & 대소문자,숫자,특수문자 포함) 검사
        if not is_valid_password(pw):
            flash("비밀번호는 최소 8자 이상이며, 대소문자, 숫자, 특수문자를 포함해야 합니다.")
            return render_template('register.html')

        try:
            cursor = dbconn.get_db().cursor(pymysql.cursors.DictCursor)
            
            # 사용자 ID 중복 체크
            cursor.execute("SELECT * FROM member WHERE MEMB_ID = %s", (id,))
            existing_user = cursor.fetchone()
            if existing_user:
                flash("이미 사용 중인 ID입니다.")
                return render_template('register.html')

            # 비밀번호 해싱
            hashed_password = generate_password_hash(pw)
            
            # 이전 비밀번호 재사용 방지
            if existing_user and check_password_hash(existing_user['MEMB_PSWD'], pw):
                flash("이전에 사용한 비밀번호는 사용할 수 없습니다.")
                return render_template('register.html')
            
            # 회원 정보 생성 SQL 쿼리 실행
            SQL = "INSERT INTO member (MEMB_ID, MEMB_PSWD, MEMB_NAME) VALUES (%s, %s, %s)"
            cursor.execute(SQL, (id, hashed_password, name))

            flash("회원가입이 완료되었습니다. 로그인해주세요.")
            # 회원 가입 완료 로깅
            logging.info(f'Successful registration for user: {id}')
            return render_template('login.html')
        except Exception as e:
            flash(f"오류가 발생했습니다! 다시 시도해주세요.")
            # 사용자 ID 중복 체크, 비밀번호 해싱, 이전 비밀번호 재사용 방지, 회원 정보 생성 쿼리 진행에서, 오류 발생 로깅
            logging.error(f'Error during registration for user: {id}: {str(e)}')
            return render_template('register.html')
        finally:
            dbconn.get_db().close()

def is_valid_password(password):
    # 비밀번호 정책: 최소 8자 & 대소문자, 숫자, 특수문자 포함
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!#%*?&])[A-Za-z\d@$!#%*?&]{8,}$"
    return re.match(pattern, password) is not None

def index():
    station_data = fetch_station_data()  # 역 데이터 로드
    return render_template('index.html', station_data=station_data)  # 렌더템플릿으로 데이터 전달

def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    return redirect(url_for('user_page.user_login_service'))