#!/usr/bin/python
# coding:utf-8
import sys

from build_rtree import ipRadixDB
from fully_update_cn import scan_cn_ip
from fully_update_fn import scan_fn_ip
from log import logger


if __name__ == '__main__':
    print 'start scan cn data ...'
    logger.info('start scan cn data ...')
    cn_done = scan_cn_ip()
    if not cn_done:
        print 'cn data exception, exit programe!'
        sys.exit(0)
    print 'start scan fn data ...'
    logger.info('start scan fn data ...')
    scan_fn_ip()

    rtree = ipRadixDB()
    #print 'loading fn data ...'
    logger.info('loading fn data ...')
    rtree.loadFromRawFile(file="output/ip_data_fn_merged")
    #print 'loading cn data ...'
    logger.info('loading cn data ...')
    rtree.loadFromRawFile(file="output/ip_data_cn_merged")
    #print 'start merge fn cn data ...'
    logger.info('start merge fn cn data ...')
    rtree.prefixMerge()
    rtree.writeRawToFile(file="output/ipdb.dat")
