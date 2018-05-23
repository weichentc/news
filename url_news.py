# -*- coding:utf8 -*-
import requests
from lxml import etree
from bs4 import  BeautifulSoup
import json
from codecs import open

res = requests.get('https://www.baidu.com/search/resources.html')
res.encoding = 'gb2312'
soup = BeautifulSoup(res.content,'html5lib')
print(soup)
urls = soup.select('li a')
url_dict = {}
for url in urls:
    link_url = url.get('href')
    domain_url = link_url.replace('http://','').replace('https://','').replace('www.','')
    name_url = url.text
    url_dict[name_url] = domain_url
print(urls)
temp = json.dumps(url_dict,ensure_ascii=False)
with open('url.text','w',encoding='utf-8') as f:
    f.write(temp)
