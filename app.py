from flask import Flask, render_template, jsonify, request, make_response, session, redirect
from flask_uuid import FlaskUUID
from config import CLIENT_ID, REDIRECT_URI, SIGNOUT_REDIRECT_URI
from controller import Oauth
import requests

import re
import datetime
import board
import comment
import json
from bs4 import BeautifulSoup
import uuid
import datetime

app = Flask(__name__)
FlaskUUID(app)

from pymongo import MongoClient

# MongoDB 접속
client = MongoClient('localhost', 27017)
# 접속할 db 명 지정 -> ddbsparta, 해당 이름의 db 가 없으면 자동 생성
db = client.fashionydb


def musinsa_scrapping():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get('https://www.musinsa.com/mz/brandsnap', headers=headers)

    # soup 에 html 형태가 그대로 들어감
    soup = BeautifulSoup(data.text, 'html.parser')

    image_trs = soup.select(
        '#wrapper > div.bottom-column.column.clearfix > div.main-content-wrapper > div.section > div > div > div.list-box.box > ul > li ')

    cnt = 0
    for tr in image_trs:
        image_tag = tr.select_one('div.articleImg > a > img')
        brandName_tag = tr.select_one('div.articleInfo > div.title > a.brand')
        modelName_tag = tr.select_one('div.articleInfo > div.title > a.name')

        if image_tag is not None:
            cnt += 1
            image_url = image_tag['src']
            brand_name = brandName_tag.text
            model_name = modelName_tag.text

            print(image_url, brand_name, model_name)

            board_uuid = uuid.uuid4()

            now = datetime.datetime.now()
            time = now.strftime('%Y-%m-%d %H:%M:%S')

            doc = {
                'board': {
                    'uuid': str(board_uuid),
                    'modelName': model_name,
                    'brandName': brand_name,
                    'imageUrl': image_url,
                    'createdAt': time,
                    'star': 0.0,
                },
                'comments': [],
                'starHistory': [],
            }

            db.brandSnaps.insert_one(doc)
            if cnt == 10:
                break


# 프로젝트 시작 시에 DB 내용을 확인하여 당일에 스크래핑 된 데이터가 있는지 확인하고
# 만약 당일에 스크래핑 된 데이터가 없다면 musinsa_scrapping() 을 호출하여 스크래핑 진행
# 만약 당일에 스크래핑 된 데이터가 있다면 아무 동작 하지 않는 함수
def call_musinsa_scrapping_one_day():
    last_data = list(db.brandSnaps.find({}, {'_id': False}).sort('board.createdAt', -1).limit(1))
    last_data_day = last_data[0]['board']['createdAt'].split(' ')[0]

    now = datetime.datetime.now()
    today = now.strftime('%Y-%m-%d')

    if last_data_day != today:
        print(f'마지막으로 스크래핑 된 날짜는 :{last_data_day} 입니다. 오늘은 {today}입니다. 스크래핑 시작 ---')
        musinsa_scrapping()
    else:
        print(f'마지막으로 스크래핑 된 날짜는 :{last_data_day} 입니다. 오늘은 {today}입니다. 스크래핑을 건너뜁니다.')


# 로그인 페이지 띄우기
@app.route("/")
def index():
    return render_template('index.html')


# 홈 페이지 띄우기
@app.route("/homepage")
def homepage():
    return render_template('homepage.html')


# 상세 페이지 띄우기
@app.route("/brandSnap/<uuid:uid>")
def detail(uid):
    return render_template('detail.html', url = uid)


# 카카오 서버로 유저 정보 요청
@app.route("/oauth")
def oauth_api():
    code = str(request.args.get('code'))

    oauth = Oauth()
    auth_info = oauth.auth(code)  # 토큰들 획득
    tokens = json.dumps({'accessToken': auth_info['access_token'], 'refreshToken': auth_info['refresh_token']})

    session['token'] = auth_info['access_token']

    # 토큰정보들
    print(auth_info)

    user = oauth.userinfo("Bearer " + auth_info['access_token'])

    return redirect('http://localhost:5000/homepage?page=1')


# 로그아웃 호출입. 세션 값 있으면 지우고 로그인 페이지로 렌더링
@app.route("/oauth/logout")
def logout():
    kakao_oauth_url = f"https://kauth.kakao.com/oauth/logout?client_id={CLIENT_ID}&logout_redirect_uri={SIGNOUT_REDIRECT_URI}"

    if session.get('token'):
        session.clear()
        value = {"status": 200, "result": "success"}
    else:
        value = {"status": 404, "result": "fail"}

    print(value)

    return redirect(kakao_oauth_url)


# 카카오 서버로 로그인 요청
@app.route('/oauth/url')
def oauth_url_api():
    return jsonify(
        kakao_oauth_url="https://kauth.kakao.com/oauth/authorize?client_id=%s&redirect_uri=%s&response_type=code" \
                        % (CLIENT_ID, REDIRECT_URI)
    )


# 카카오 서버로 유저 정보 요청 url 매핑
@app.route("/oauth/userinfo", methods=['POST'])
def oauth_userinfo_api():
    access_token = request.get_json()['access_token']
    result = Oauth().userinfo("Bearer " + access_token)
    return jsonify(result)


# access_token 을 이용하여 카카오 서버로 유저 정보 요청
def token_user_info(access_token):
    user_info = Oauth().userinfo("Bearer " + access_token)
    return user_info


# 전체 게시물에 대한 정보를 내려주는 API
@app.route('/api/board', methods=['GET'])
def board_entire_show():
    response = board.board_entire_show()
    return jsonify(response)


# 게시물에 대한 상세 정보를 내려주는 API
@app.route('/api/board/<uuid:uid>', methods=['GET'])
def board_detail_show(uid):
    response = board.board_detail_show(uid)
    return jsonify(response)


# 댓글 등록 API
@app.route('/api/board/<uuid:uid>/comment', methods=['POST'])
def comment_enroll(uid):
    response = comment.comment_enroll(uid)
    return jsonify(response)

# 별점 등록 API
@app.route('/api/board/<uuid:uid>/star', methods=['POST'])
def board_star_enroll(uid):
    response = board.star_enroll(uid)
    return jsonify(response)


if __name__ == "__main__":
    call_musinsa_scrapping_one_day()
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run('0.0.0.0', port=5000, debug=True)
