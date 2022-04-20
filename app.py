from flask import Flask, render_template, jsonify, request
import re
import datetime
import json

app = Flask(__name__)

from pymongo import MongoClient

# MongoDB 접속
client = MongoClient('localhost', 27017)
# 접속할 db 명 지정 -> dbsparta, 해당 이름의 db 가 없으면 자동 생성
db = client.fashionydb


@app.route('/api/board', methods=['GET'])
def board_entire_show():
    page = int(request.args.get('page'))
    page_size = int(request.args.get('pageSize'))
    boards = list(db.brandSnaps.find({}, {'id_': False}).skip((page - 1) * page_size).limit(page_size))

    response = {
        'data': {
            'boards': boards
        }
    }
   
    return json.dumps(response, default=str)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
