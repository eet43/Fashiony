from flask import Flask, render_template, jsonify, request
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


def comment_enroll(uid):
    now = datetime.datetime.now()
    time = now.strftime('%Y-%m-%d %H:%M:%S')

    access_token = request.headers['Access-Token']
    token_user_info = app.token_user_info(access_token)

    user_name = token_user_info['properties']['nickname']

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
