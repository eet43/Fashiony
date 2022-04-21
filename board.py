from flask import Flask, render_template, jsonify, request, session
import re
import datetime
import json
import app

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

    if request.args.get('search') is not None or request.args.get('search') is '':
        search = ".*" + request.args.get('search') + ".*"
        like_search = re.compile(search, re.IGNORECASE)
        boards = list(
            db.brandSnaps.find({"$or": [{'board.modelName': like_search}, {'board.brandName': like_search}]},
                               {'_id': False}).skip(
                (page - 1) * page_size).limit(page_size))
        count = len(list(
            db.brandSnaps.find({"$or": [{'board.modelName': like_search}, {'board.brandName': like_search}]},
                               {'_id': False})))
    else:
        boards = list(db.brandSnaps.find({}, {'_id': False}).skip((page - 1) * page_size).limit(page_size))
        count = len(list(db.brandSnaps.find({}, {'_id': False})))

    now = datetime.datetime.now()
    time = now.strftime('%Y-%m-%d %H:%M:%S')

    response = {
        'time': time,
        'total': count,
        'data': {
            'boards': boards
        }
    }

    return response


# 게시물 상세 정보를 내려 주는 API
def board_detail_show(uid):
    now = datetime.datetime.now()
    time = now.strftime('%Y-%m-%d %H:%M:%S')

    board = db.brandSnaps.find_one({'board.uuid': str(uid)}, {'_id': False})
    if board is None:
        response = {
            'time': time,
            'error': 'the post in that uuid does not exist',
        }
        return response

    response = {
        'time': time,
        'data': board
    }
    return response


# 게시물의 별점을 등록하는 API
def star_enroll(uid):
    board = db.brandSnaps.find_one({'board.uuid': str(uid)}, {'_id': False})

    access_token = session['token']
    token_user_info = app.token_user_info(access_token)

    user_name = token_user_info['properties']['nickname']

    now = datetime.datetime.now()
    time = now.strftime('%Y-%m-%d %H:%M:%S')

    data = json.loads(request.data)
    star = data['star']

    if board is None:
        response = {
            'time': time,
            'error': 'the post in that uuid does not exist',
        }
        return response

    if user_name is None or user_name is "":
        response = {
            'time': time,
            'error': 'unable to receive user information',
        }
        return response

    if star is None or str(type(star)) != "<class 'int'>":
        response = {
            'time': time,
            'error': 'unable to receive star',
        }
        return response

    star_history = list(board['starHistory'])

    insert_star = {
        'userName': user_name,
        'star': star,
        'createdAt': time,
    }

    star_history.append(insert_star)

    db.brandSnaps.update_one({'board.uuid': str(uid)}, {'$set': {'starHistory': star_history}})

    board = db.brandSnaps.find_one({'board.uuid': str(uid)}, {'_id': False})

    update_star_history = list(board['starHistory'])

    sum = 0.0
    for star_history in update_star_history:
        sum += star_history['star']

    ave = float(sum / len(update_star_history))

    db.brandSnaps.update_one({'board.uuid': str(uid)}, {'$set': {'board.star': ave}})

    board = db.brandSnaps.find_one({'board.uuid': str(uid)}, {'_id': False})

    response = {
        'time': time,
        'data': board
    }

    return response

