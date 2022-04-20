from flask import Flask, render_template, jsonify, request, make_response
from flask_uuid import FlaskUUID
from config import CLIENT_ID, REDIRECT_URI
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


def create_access_token(identity):
    pass


# 카카오 서버로 유저 정보 요청
@app.route("/oauth")
def oauth_api():
    code = str(request.args.get('code'))

    oauth = Oauth()
    auth_info = oauth.auth(code)
    user = oauth.userinfo("Bearer " + auth_info['access_token'])

    resp = make_response(render_template('example.html'))
    return resp


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


# 전체 게시물에 대한 정보를 내려주는 API
@app.route('/api/board', methods=['GET'])
def board_entire_show():
    response = board.board_entire_show()
    return jsonify(response)


# 댓글 등록 API
@app.route('/api/board/<uuid:uid>/comment', methods=['POST'])
def comment_enroll(uid):
    response = comment.comment_enroll(uid)
    return jsonify(response)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
