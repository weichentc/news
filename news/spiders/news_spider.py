# -*- coding:utf8 -*-
import scrapy
from scrapy.selector import HtmlXPathSelector
import random
import hashlib
import base64
from news.items import NewsItem
import time
from scrapy.exceptions import DropItem
import redis
from codecs import open
import json
import re

class NewsSpider(scrapy.Spider):

    with open('./url.text','r',encoding='utf-8') as f:
        r = f.readline()
        url_dict = json.loads(r)
        # print(url_dict)
        url_list = []
    for url in url_dict.values():
        url_list.append(url)
    url_list.append('news.baidu.com')
    name = "news"
    allowed_domains = url_list
    # print(allowed_domains)
    # allowed_domains = ['eastmoney.com']

    start_urls = [
        # "http://news.baidu.com/",
        'https://www.baidu.com/search/resources.html'
        # "http://www.dmoz.org/Computers/Programming/Languages/Python/Resources/"
    ]

    def __init__(self):
        self.redis_db = redis.Redis(host='127.0.0.1', port=6379, db=4) #连接redis，相当于MySQL的conn
        self.redis_data_now_dict = 'url_now'
        self.redis_db.flushdb()
        self.list_url_useless = ['#','/','javascript:','null','javascript:void(0)','#1','javascript:void(0);','javascript:;']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        # newurls = hxs.select('//a/@href').extract()
        newurls = response.xpath('//a/@href').extract()
        print('url_now: ',response.url)
        # print('len_urls:',len(newurls))
        list_part = response.url.split('/')
        if list_part[-1] == '':
            list_part = list_part[:-1]
        # if len(list_part) > 4 and (len(list_part[-1]) >10):
        if response.url.endswith('.html') and self.hasNumbers(list_part[-1]):
            filename = hashlib.md5(response.url.encode('utf-8')).hexdigest()+ '.txt'
            # print('filename: ',filename)
            last_update_time = time.strftime("%Y-%m-%d %H:%M:%S")
            item = NewsItem()
            item['url'] = response.url
            item['contents'] = response.body
            item['filename'] = filename
            item['last_update_time'] = last_update_time
            yield item


        for url in newurls:
            if url in self.list_url_useless:
                continue
            if url.startswith('//'):
                url = 'http://' + url
            elif 'http' not in url:
                # print('url1: ',url)
                url = 'http://' + response.url.split('/')[2] + url
            if response.url.endswith('.html') and len(list_part) > 5:
                continue
            yield scrapy.Request(url,callback=self.parse,dont_filter=False)

            # # print('item: ',item)
            # # with open('./contents/' +filename, 'wb') as f:
            # #     f.write(response.body)
    def hasNumbers(self, inputString):
        return bool(re.search(r'\d', inputString))
