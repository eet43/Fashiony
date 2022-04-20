from flask import Flask, render_template, jsonify, request
import re
import datetime
import json

from pymongo import MongoClient

# MongoDB 접속
client = MongoClient('localhost', 27017)
# 접속할 db 명 지정 -> dbsparta, 해당 이름의 db 가 없으면 자동 생성
db = client.fashionydb


# 전체 게시물에 대한 정보를 내려주는 API
def board_entire_show():
    if request.args.get('page') is not None:
        page = int(request.args.get('page'))
    else:
        page = 1
    if request.args.get('pageSize') is not None:
        page_size = int(request.args.get('pageSize'))
    else:
        page_size = 10

    if request.args.get('search') is not None:
        search = request.args.get('search')
        like_search = re.compile(f'.*${search}.*', re.IGNORECASE)
        boards = list(
            db.brandSnaps.find({"$or": [{'modelName': like_search}, {'brandName': like_search}]}, {'id_': False}).skip(
                (page - 1) * page_size).limit(page_size))
    else:
        boards = list(db.brandSnaps.find({}, {'id_': False}).skip((page - 1) * page_size).limit(page_size))

    now = datetime.datetime.now()
    time = now.strftime('%Y-%m-%d %H:%M:%S')

    response = {
        'time': time,
        'data': {
            'boards': boards
        }
    }

    return response
