from flask import Flask, render_template, jsonify, request
from flask_uuid import FlaskUUID
import re
import datetime
import board
import comment

app = Flask(__name__)
FlaskUUID(app)

from pymongo import MongoClient

# MongoDB 접속
client = MongoClient('localhost', 27017)
# 접속할 db 명 지정 -> dbsparta, 해당 이름의 db 가 없으면 자동 생성
db = client.fashionydb


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
