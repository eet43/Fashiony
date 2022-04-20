from flask import Flask, render_template, jsonify, request, make_response
from config import CLIENT_ID, REDIRECT_URI
from controller import Oauth

import re
import datetime
import json
import board

app = Flask(__name__)

from pymongo import MongoClient


# MongoDB 접속
client = MongoClient('localhost', 27017)
# 접속할 db 명 지정 -> dbsparta, 해당 이름의 db 가 없으면 자동 생성
db = client.fashionydb

@app.route("/")
def index():
    return render_template('index.html')


def create_access_token(identity):
    pass


@app.route("/oauth")
def oauth_api():

    code = str(request.args.get('code'))

    oauth = Oauth()
    auth_info = oauth.auth(code)
    user = oauth.userinfo("Bearer " + auth_info['access_token'])

    resp = make_response(render_template('example.html'))
    return resp

@app.route('/oauth/url')
def oauth_url_api():
    """
    Kakao OAuth URL 가져오기
    """
    print('-------------')
    return jsonify(
        kakao_oauth_url="https://kauth.kakao.com/oauth/authorize?client_id=%s&redirect_uri=%s&response_type=code" \
                        % (CLIENT_ID, REDIRECT_URI)
    )

@app.route("/oauth/userinfo", methods=['POST'])
def oauth_userinfo_api():
    """kakao에서 해당 유저의 실제 Userinfo를 가져옴
    """
    access_token = request.get_json()['access_token']
    result = Oauth().userinfo("Bearer " + access_token)
    return jsonify(result)


# 전체 게시물에 대한 정보를 내려주는 API
@app.route('/api/board', methods=['GET'])
def board_entire_show():
    response = board.board_entire_show()
    return jsonify(response)

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

