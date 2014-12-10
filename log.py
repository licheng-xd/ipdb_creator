#coding:utf-8
import logging
import os

#output to console and log file

def get_logger(filepath):
	formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
	hdlr = logging.FileHandler(filepath)
	hdlr.setFormatter(formatter)

	console = logging.StreamHandler()
	console.setFormatter(formatter)

	logger = logging.getLogger()
	logger.addHandler(hdlr)
	logger.addHandler(console)
	logger.setLevel(logging.INFO)

	#disable requests log
	requests_log = logging.getLogger("requests")
	requests_log.setLevel(logging.WARNING)

	return logger

def info(msg):
	logger.info(msg)

def error(msg):
	logger.info(msg)

def debug(msg):
	logger.info(msg)

def warn(msg):
	logger.warn(msg)

logger = get_logger(os.getcwd() + '/log/ipdb.log')