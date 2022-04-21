from flask import Flask, render_template, jsonify, request, make_response, session, redirect
from flask_uuid import FlaskUUID
from config import CLIENT_ID, REDIRECT_URI, SIGNOUT_REDIRECT_URI
from controller import Oauth

import re
import datetime
import board
import comment
import json

app = Flask(__name__)
FlaskUUID(app)

from pymongo import MongoClient

# MongoDB 접속
client = MongoClient('localhost', 27017)
# 접속할 db 명 지정 -> dbsparta, 해당 이름의 db 가 없으면 자동 생성
db = client.fashionydb


# 로그인 페이지 띄우기
@app.route("/")
def index():
    return render_template('index.html')


# 홈 페이지 띄우기
@app.route("/homepage")
def homepage():
    return render_template('homepage.html')


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

@app.route("/homepage")
def homepage():
    return render_template('homepage.html')


if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run('0.0.0.0', port=5000, debug=True)
