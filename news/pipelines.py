# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import redis
from scrapy.conf import settings
import pymongo
import pandas as pd  #用来读MySQL
# import mysql.connector
from scrapy.exceptions import DropItem

redis_db = redis.Redis(host='127.0.0.1', port=6379, db=4) #连接redis，相当于MySQL的conn
redis_data_dict = "url_news"  #key的名字，写什么都可以，这里的key相当于字典名称，而不是key值。
# redis_data_now_dict = 'url_now'


class NewsPipeline(object):
    # def process_item(self, item, spider):
    #     return item

    def __init__(self):
        port = settings['MONGODB_PORT']
        host = settings['MONGODB_HOST']
        db_name = settings['MONGODB_DBNAME']
        client = pymongo.MongoClient(host=host, port=port)
        db = client[db_name]
        self.post = db[settings['MONGODB_DOCNAME']]
        ## self.urls = db[settings['MONGODB_DOCNAME']].find({},{'url':1})
        ## print(self.urls)
        # redis_db.flushdb()

    def process_item(self, item, spider):
        # if redis_db.hexists(redis_data_now_dict,item['url']):
        #     # print('same_url_now: ',item['url'])
        #     raise DropItem("Dupliicate item found: %s" % item)
        book_info = dict(item)
        self.post.insert(book_info)
        # print('item[url]: ',item['url'])
        # redis_db.hset(redis_data_now_dict,item['url'],0)
        # print('url_to_mongo: ',item['url'])
        # self.urls_now.add(item['url'])
        # print('len_url_now: ',len(redis_db[redis_data_now_dict]))
        return item

class Checkurl2Pipeline(object):
    # conn = mysql.connector.connect(user = 'root', password='yourpassword', database='dbname', charset='utf8')

    def __init__(self):
        port = settings['MONGODB_PORT']
        host = settings['MONGODB_HOST']
        db_name = settings['MONGODB_DBNAME']
        client = pymongo.MongoClient(host=host, port=port)
        db = client[db_name]
        self.post = db[settings['MONGODB_DOCNAME']]
        self.urls = db[settings['MONGODB_DOCNAME']].find({},{'url':1})
        redis_db.flushdb() #删除全部key，保证key为0，不然多次运行时候hlen不等于0，刚开始这里调试的时候经常出错。
        if redis_db.hlen(redis_data_dict) == 0: #
            for url in self.urls: #把每一条的值写入key的字段里
                # print('url: ',url['url'])
                url = url['url']
                redis_db.hset(redis_data_dict, url, 0) #把key字段的值都设为0，你要设成什么都可以，因为后面对比的是字段，而不是值。


    def process_item(self, item, spider):
        if redis_db.hexists(redis_data_dict, item['url']): #取item里的url和key里的字段对比，看是否存在，存在就丢掉这个item。不存在返回item给后面的函数处理
            # print('same_url: ',item['url'])
            raise DropItem("Duplicate item found: %s" % item)
        else:
            return item
#from scrapy.exceptions import DropItem

class Checkurl1Pipeline(object):

    def __init__(self):
        self.urls_now = set()
        redis_db.flushdb()

    def process_item(self, item, spider):
        # if item['url'] in self.urls_now:
        if redis_db.hexists(redis_data_now_dict,item['url']):
            # print('same_url_now: ',item['url'])
            raise DropItem("Dupliicate item found: %s" % item)
        else:
            redis_db.hset(redis_data_now_dict,item['url'],0)
            # self.urls_now.add(item['url'])
            # print('len_url_now: ',len(redis_db[redis_data_now_dict]))
            return item

# class NewsPipeline(object):
#     def process_item(self, item, spider):
#         return item

