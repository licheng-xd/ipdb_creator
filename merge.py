# coding:utf-8

from build_rtree import ipRadixDB
from log import logger

if __name__ == '__main__':
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
    rtree.writeRawToFile(file="output/ipdb-all.dat")
