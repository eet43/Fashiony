from flask import Flask, render_template, jsonify, request, session
import re
import datetime
import uuid
import json
import app

from pymongo import MongoClient

# MongoDB 접속
client = MongoClient('localhost', 27017)
# 접속할 db 명 지정 -> dbsparta, 해당 이름의 db 가 없으면 자동 생성
db = client.fashionydb


# 댓글 등록 API
def comment_enroll(uid):
    now = datetime.datetime.now()
    time = now.strftime('%Y-%m-%d %H:%M:%S')

    access_token = session['token'] #세션에서 토큰 값 가져오기
    token_user_info = app.token_user_info(access_token) #토큰 값으로 유저 정보 받아오기

    user_name = token_user_info['properties']['nickname'] #유저 정보에서 이름 받아오기

    data = json.loads(request.data)
    content = data['content']

    if user_name is None or user_name is "":
        response = {
            'time': time,
            'error': 'unable to receive user information',
        }
        return response

    if content is None or content is "":
        response = {
            'time': time,
            'error': 'unable to receive content',
        }
        return response

    comment_uuid = uuid.uuid4()

    insert_comment = {
        'uuid': str(comment_uuid),
        'userName': user_name,
        'content': content,
        'createdAt': time,
        'updatedAt': time
    }

    board = db.brandSnaps.find_one({'board.uuid': str(uid)}, {'_id': False})
    if board is None:
        response = {
            'time': time,
            'error': 'the post in that uuid does not exist',
        }
        return response

    comments = list(board['comments'])
    comments.append(insert_comment)

    db.brandSnaps.update_one({'board.uuid': str(uid)}, {'$set': {'comments': comments}})

    board = db.brandSnaps.find_one({'board.uuid': str(uid)}, {'_id': False})

    response = {
        'time': time,
        'data': board
    }

    return response
