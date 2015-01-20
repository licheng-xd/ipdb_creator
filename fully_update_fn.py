#coding:utf-8
from query import query_ip
import random
from netaddr import IPRange, IPNetwork, IPSet
from collections import defaultdict
from build_rtree import  ipRadixDB
import time
from log import logger


def ip_integer_from_string(s):
    "Convert dotted IPv4 address to integer."
    return reduce(lambda a,b: a<<8 | b, map(int, s.split(".")))

def ip_integer_to_string(ip):
     "Convert 32-bit integer to dotted IPv4 address."
     return ".".join(map(lambda n: str(ip>>n & 0xFF), [24,16,8,0]))

def ip_integer_to_integer_array(ip):
    "convert 32-bit integer to [a, b, c, d]"
    return map(lambda n: ip>>n & 0xff, [24,16,8,0])

def generate_random_ip(network, masklen):
    random_int = random.randint(0, (1<<(32-masklen)) -1)
    return ip_integer_to_string(ip_integer_from_string(network) + random_int)

def generate_random_ip_splited(network, masklen, splited_num, splited_order):
    splited_size = (1<<(32-masklen))/splited_num
    random_int = random.randint(splited_size*splited_order,splited_size*(splited_order+1) - 1)
    return ip_integer_to_string(ip_integer_from_string(network) + random_int)

def split_network_from_start_to_end(start, end):
    ip = IPRange(start, end)
    return map(lambda net:(str(net.network), net.prefixlen, net.size), ip.cidrs())


def scan_fn_ip():
    country_code = {}
    for line in open('input/country_code', 'r'):
        code, name = line.split(" ")
        country_code[code] = name.strip().decode("utf-8")
        logger.info(code + ' ' + country_code[code])

    rtree = ipRadixDB()
    ip_area_list = ["input/delegated-arin-latest", "input/delegated-ripencc-latest", "input/delegated-lacnic-latest", "input/delegated-afrinic-latest", "input/delegated-apnic-latest"]
    dft = defaultdict(list)
    availableIPs = []
    for f in ip_area_list:
        seed_file = open(f,'r')
        for l in seed_file.readlines():
            params = l.split('|')
            if len(params) >= 4 and params[2] == "ipv4" and params[3] != "*" and params[1] != "CN":
                startIP = params[3]
                endIP = ip_integer_to_string(ip_integer_from_string(startIP) + int(params[4]) - 1)
                logger.info(startIP + ' ' + endIP + ' ' + params[4])
                iprange = IPRange(startIP, endIP)
                if params[1] == '':
                    availableIPs += map(str, iprange.cidrs())
                else:
                    dft[params[1]] += map(str, iprange.cidrs())
    for key in dft:
        prefix = dft[key][-1]
        network,masklen = prefix.split('/')
        masklen = int(masklen)
        ip = generate_random_ip(network,masklen)
        ipset = IPSet(dft[key])
        for prefix in ipset.iter_cidrs():
            network,masklen = str(prefix).split('/')
            masklen = int(masklen)
            rtree.addPrefix(network,masklen)
            data = rtree.rnode.data
            country = country_code[key]
            logger.info(str(prefix) + ' ' + country)
            data['country'] = country #jsonData.get('country','')
            data['ip'] = ip
            data['ip_amount'] = prefix.size
            data['province'] = ''
            data['city'] = ''
            data['isp'] = ''
    for prefix in availableIPs:
        network,masklen = prefix.split("/")
        masklen = int(masklen)
        ip = generate_random_ip(network,masklen)
        jsonData = None;
        while jsonData == None:
            try:
                jsonData = query_ip(ip)
            except Exception, e:
                logger.error(e)
                time.sleep(0.5)
        rtree.addPrefix(network,masklen)
        data = rtree.rnode.data
        data['country'] = jsonData.get('country','')
        data['ip'] = ip
        data['ip_amount'] = IPNetwork(prefix).size
        data['province'] = ''
        data['city'] = ''
        data['isp'] = ''
        logger.info(prefix + ' ' + data['country'])
    logger.info('start merge fn data ...')
    rtree.writeRawToFile(file="output/ip_data_fn_original")
    rtree.prefixMerge()
    rtree.writeRawToFile(file="output/ip_data_fn_merged")

if __name__ == '__main__':
    scan_fn_ip()
