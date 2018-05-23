# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import base64
from proxy import get_proxy
import redis
from scrapy.conf import settings
from scrapy.exceptions import IgnoreRequest
import pymongo
import time
redis_db = redis.Redis(host='127.0.0.1', port=6379, db=4) #连接redis，相当于MySQL的conn
redis_data_dict = "url_news"  #key的名字，写什么都可以，这里的key相当于字典名称，而不是key值。
# redis_data_now_dict = 'url_now'

class NewsSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class ProxyMiddleware(object):
    # overwrite process request
    def process_request(self, request, spider):
        # print(time.strftime('%H:%M:%S'))
        proxy_config = get_proxy(keep_ip=False)['proxy']
        # kwargs['proxies'] = {'http': 'http://%(user)d:%(pwd)s@%(proxy)s' % proxy_config,
        # print(proxy_config)
        # print(time.strftime('%H:%M:%S'))
        # print('proxy_config: ',proxy_config)
        # request.meta['proxies'] = {'http': 'http://%(user)d:%(pwd)s@%(proxy)s' % proxy_config,
        #                      'https': 'https://%(user)d:%(pwd)s@%(proxy)s' % proxy_config}
        # 设置代理的主机和端口号
        # request.meta['proxy'] = 'http://%s:%d/get-proxy-api' % ('118.190.114.196',8080)
        # print('proxy_config: ',proxy_config)
        if proxy_config:
            request.meta['proxy'] = 'http://%s' % proxy_config

class CheckurlMiddleware(object):

    def __init__(self):
        self.redis_db = redis.Redis(host='127.0.0.1', port=6379, db=5) #连接redis，相当于MySQL的conn
        self.redis_data_dict = "url_news"  #key的名字，写什么都可以，这里的key相当于字典名称，而不是key值。
        # self.redis_data_now_dict = 'url_now'
        # self.urls_now = set()
        self.redis_db.flushdb()
        # print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        port = settings['MONGODB_PORT']
        host = settings['MONGODB_HOST']
        db_name = settings['MONGODB_DBNAME']
        client = pymongo.MongoClient(host=host, port=port)
        db = client[db_name]

        self.post = db[settings['MONGODB_DOCNAME']]
        self.urls = db[settings['MONGODB_DOCNAME']].find({},{'url':1})
        redis_db.flushdb() #删除全部key，保证key为0，不然多次运行时候hlen不等于0，刚开始这里调试的时候经常出错。
        if redis_db.hlen(redis_data_dict) == 0: #
            # print('len_urls: ',len(self.urls))
            num = 0
            for url in self.urls: #把每一条的值写入key的字段里
                # print('url: ',url['url'])
                num += 1
                url = url['url']
                redis_db.hset(redis_data_dict, url, 0) #把key字段的值都设为0，你要设成什么都可以，因为后面对比的是字段，而不是值。
            print('num: ',num)
    def process_request(self, request, spider):
        # if item['url'] in self.urls_now:
        if self.redis_db.hexists(self.redis_data_dict,request.url):
            # print('same_url_now: ',item['url'])
            raise IgnoreRequest("IgnoreRequest : %s" % request.url)
        # else:
        #     self.redis_db.hset(self.redis_data_dict,request.url,0)
