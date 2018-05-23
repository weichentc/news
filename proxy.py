# _*_ coding: utf-8 _*_

import time
import requests
import re
import os
# from gs.SpiderMan import SpiderMan
import json

manager_host = '118.190.114.196'
manager_port = 8080

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': 'samr.cfda.gov.cn',
    'If-Modified-Since': 'Mon, 09 Apr 2018 06:45:30 GMT',
    'Referer': 'http://samr.cfda.gov.cn/WS01/CL1667',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0',
}
expected_ip = {}
# class Proxy():
#     def __init__(self):
#         self.expect_ip =
def get_proxy(keep_ip=False):
    global  expected_ip
    # print('expected_ip: ',expected_ip)
    try:
        url = 'http://%s:%d/get-proxy-api' % (manager_host, manager_port)
        params = {'order': '5fe6cf97-5592-11e7-be16-f45c89a63279'}
        # print('expected_ip:',expected_ip)
        if keep_ip:
            if expected_ip:
                return  expected_ip
        res = requests.get(url, params=params)
        # print res.text
        if res.status_code == 200 and res.text != '{}':
            json_obj = json.loads(res.text)
            # print(json_obj['proxy'])
            if keep_ip:
                expected_ip['proxy'] = json_obj['proxy'].split(':')[0]
            return json_obj
    except:
        return None
def get_request(url, session = None,headers=None,keep_ip=False,**kwargs):
    global expected_ip
    for t in range(3):
        proxy_config = get_proxy(keep_ip=keep_ip)
        expected_ip = proxy_config['proxy'].split(':')[0]
        # print json.dumps(proxy_config, ensure_ascii=False, indent=4)
        kwargs['proxies'] = {'http': 'http://%(user)d:%(pwd)s@%(proxy)s' % proxy_config,
                             'https': 'https://%(user)d:%(pwd)s@%(proxy)s' % proxy_config}
        # print(kwargs['proxies'])
        # kwargs['timeout'] = proxy_config['timeout']
        # kwargs.setdefault('headers', {})
        # kwargs['headers']['Connection'] = 'close'
        # kwargs['headers']['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0'
        # kwargs['headers'] = headers
        if headers:
            kwargs['headers'] = headers
        try:
            if session:
                # r=requests.get(url=url, **kwargs)
                r = session.get(url=url, **kwargs)
            else:
                r = requests.get(url=url,allow_redirects=False, **kwargs)
                # r = requests.get(url=url, **kwargs)
            # print('r: ',r.content)
            if 'The cache was not able to resolve the hostname presented in the URL' in r.text:
                raise requests.exceptions.RequestException()
            else:
                return r
        except Exception as e:
            raise e


if __name__ == '__main__':
        pass
