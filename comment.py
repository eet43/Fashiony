from flask import Flask, render_template, jsonify, request
import re
import datetime
import board

from pymongo import MongoClient

# MongoDB 접속
client = MongoClient('localhost', 27017)
# 접속할 db 명 지정 -> dbsparta, 해당 이름의 db 가 없으면 자동 생성
db = client.fashionydb

def comment_enroll():
    user_name = request.form['user_name']
    content = request.form['content']
    