#!/usr/bin/python3
# -*- coding: utf-8 -*-

import requests
import sys
import os
from log import logger

base_taobao_url = "http://ip.taobao.com/service/getIpInfo.php"
base_sina_url = "http://int.dpool.sina.com.cn/iplookup/iplookup.php"

def query_ip(ip, base_url = None):
    if base_url == None:
        url_list = [ base_taobao_url, base_sina_url ]
    else:
        url_list = [ base_url ]
    payload = {"ip":ip}
    resultL = []
    for url in url_list:
        if url == base_sina_url:
            payload["format"] = "json"
        else:
            payload.pop("format", 0)
        result = requests.get(url, params=payload)
        if result.status_code == 200:
            json = result.json()
            if url == base_taobao_url and not json["code"]:
                resultL.append(json["data"])
            if url == base_sina_url and json["ret"] == 1:
                resultL.append(json)
        else:
            #print "There is an error, maybe too many requests per second."
            logger.info("There is an error, maybe too many requests per second.")
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
        ip = "199.19.226.150"
    print query_ip(ip, base_sina_url)
