# -*- coding:utf-8 -*-
from pymongo import MongoClient
import re


conn = MongoClient('127.0.0.1',27017)
db = conn.news
my_set = db.news1

# for i in my_set.find({},{'url':1}):
#     last_url = i['url'].split('/')[-1]
#     if  not bool(re.search(r'\d',last_url)):
#         print(i['url'])

for i in my_set.find({},{'contents':1}):
    print(i)