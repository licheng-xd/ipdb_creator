#coding:utf-8
from query import *
import random
import math
from netaddr import IPRange, IPNetwork, IPSet
from build_rtree import ipRadixDB
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


def scan_cn_ip():
    rtree = ipRadixDB()
    all_done = True
    f = open("input/delegated-apnic-latest","r")
    count = 0
    try:
        for line in f.readlines():
            if count % 100 == 0:
                logger.info("==============================>[%s]", str(count))
            count += 1
            #l = line.decode("utf-8")
            params = line.split("|")
            if len(params) >=4 and params[1] == 'CN' and params[2] == "ipv4" and params[3] != "*":
                network = params[3]
                prefixlen = 32 - int(math.log(int(params[4]), 2))
                prefix = network + '/' + str(prefixlen)
                if int(prefixlen) > 24:
                    networks = IPNetwork(network+'/'+'24')
                    subnetworks = networks.subnet(24)
                else:
                    networks = IPNetwork(prefix)
                    subnetworks = networks.subnet(24)
                for sub in subnetworks:
                    network, prefixlen = str(sub).split("/")
                    ip = generate_random_ip(network, int(prefixlen))
                    
                    rtree.addPrefix(network, int(prefixlen))
                    jsonData = query_local(ip)
                    data_key = ["country", "province", "city", "isp"]
                    node  = rtree.rnode
                    for key in data_key:
                        node.data[key] = jsonData.get(key,"")
                    node.data["ip"] = ip
                    logger.info("%s [%s] [%s] [%s]" % (ip, prefix, str(sub), node.data["province"]))

    except Exception, e:
        logger.error(e)
        all_done = False
    finally:
        if all_done:
            rtree.writeRawToFile(file="output/ip_data_cn_original")
            rtree.prefixMerge()
            rtree.writeRawToFile(file="output/ip_data_cn_merged")
        else:
            logger.info("finish count=" + str(count))
            rtree.writeRawToFile(file="output/ip_data_cn_original_" + str(count))
        return all_done
if __name__ == '__main__':
    scan_cn_ip()
