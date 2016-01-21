#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import sys
from time import sleep
from log import logger
import os, json

from ipip import IP

base_taobao_url = "http://ip.taobao.com/service/getIpInfo.php"
base_sina_url = "http://int.dpool.sina.com.cn/iplookup/iplookup.php" # 新浪库准确率太低，抛弃他

IP.load(os.path.abspath("input/mydata4vipweek2.dat"))

def query_local(ip):
    ret = IP.find(ip)
    tmp = ret.split()
    print tmp[0], tmp[1]
    rjson = dict()
    if tmp[0] != u'中国':
        rjson["country"] = u'中国'
        rjson["province"] = u'北京市'
        rjson["city"] = u'北京市'
        rjson["isp"] = tmp[-1]
    else:
        # if tmp[1] == u'台湾' or tmp[1] == u'香港' or tmp[1] == u'澳门':
        if tmp[1] in (u'台湾', u'香港', u'澳门'):
            rjson["country"] = tmp[1]
            rjson["province"] = u''
            rjson["city"] = u''
            rjson["isp"] = u''
        elif tmp[1] in (u'西藏', u'内蒙古'):
            rjson["country"] = tmp[0]
            rjson["province"] = tmp[1] + u'自治区'
            rjson["city"] = tmp[-2] + u'市'
            rjson["isp"] = tmp[-1]
        elif tmp[1] == u'广西':
            rjson["country"] = tmp[0]
            rjson["province"] = tmp[1] + u'壮族自治区'
            rjson["city"] = tmp[-2] + u'市'
            rjson["isp"] = tmp[-1]
        elif tmp[1] == u'新疆':
            rjson["country"] = tmp[0]
            rjson["province"] = tmp[1] + u'维吾尔自治区'
            rjson["city"] = tmp[-2] + u'市'
            rjson["isp"] = tmp[-1]
        elif tmp[1] == u'宁夏':
            rjson["country"] = tmp[0]
            rjson["province"] = tmp[1] + u'回族自治区'
            rjson["city"] = tmp[-2] + u'市'
            rjson["isp"] = tmp[-1]
        else:
            rjson["country"] = tmp[0]
            rjson["province"] = tmp[1] + u'省'
            rjson["city"] = tmp[-2] + u'市'
            rjson["isp"] = tmp[-1]
    return rjson

def query_ip(ip):
    payload = {"ip":ip}
    resultL = []
    while True:
        try:
            payload.pop("format", 0)
            result = requests.get(base_taobao_url, params=payload, timeout=5)
            if result.status_code == 200:
                json = result.json()
                resultL.append(json["data"])
                break
            else:
                logger.warn("request ip.taobao error, maybe too many requests, let's wait a while")
                sleep(1)
        except Exception, e:
            logger.error("request taobao exception: " + str(e.message))

    if resultL:
        rjson = reduce(lambda d1,d2: dict(d1.items() + { k:v for k,v in d2.items() if v }.items()), resultL)
    else:
        rjson = reduce(lambda d1,d2: dict(d1.items() + { k:v for k,v in d2.items() if v }.items()), resultL,{})
    if rjson:
        if not rjson.get("province", ""):
            rjson["province"] = rjson.get("region", "")
            rjson["city"] = rjson.get("city", "")
            rjson["isp"] = rjson.get("isp", "")
        #print rjson
        return rjson

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        ip = sys.argv[1]
    else:
        ip = "111.126.0.1"
    print json.dumps(query_local(ip)).decode("unicode-escape")
