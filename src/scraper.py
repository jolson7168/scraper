#!/usr/bin/env python

from __future__ import print_function      # get latest print functionality

import urllib2
import re
import logging
import sys
import time               # sleep function for connection back-off
import json               # JSON object encoding/decoding

from ConfigParser import RawConfigParser

def currentDayStr():
    return time.strftime("%Y%m%d")

def currentTimeStr():
    return time.strftime("%H:%M:%S")

def initLog(rightNow):
    logger = logging.getLogger(cfg.get('logging', 'logname'))
    logPath=cfg.get('logging', 'logPath')
    logFilename=cfg.get('logging', 'logFileName')
    hdlr = logging.FileHandler(logPath+rightNow+logFilename)
    formatter = logging.Formatter(cfg.get('logging', 'logFormat'),cfg.get('logging', 'logTimeFormat'))
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr) 
    logger.setLevel(logging.INFO)
    return logger


def grabTag(html,openTag, closeTag, eliminate):
	result=re.search(openTag+'(.*)'+closeTag, html)
	if hasattr(result, 'group'):
		return result.group(1).replace(eliminate,"")
	else:
		return "Null"



def getCmdLineParser():
    import argparse
    desc = 'Execute coverage test cases'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-c', '--config_file', default='../config/scrape_config',
                        help='configuration file name (*.ini format)')

    parser.add_argument('-i', '--input_file', default='../data/scrape.json', 
                        help='data input file name')

    parser.add_argument('-o', '--output_file', default='../data/scraped.csv', 
                        help='data output file name')

    return parser

def scrapeIt(scrapeObj):
	response = urllib2.urlopen(scrapeObj["url"])
	html = response.read()
	for thisTag in scrapeObj["get"]:
		eliminate=""
		if "eliminate" in thisTag:
			eliminate=thisTag["eliminate"]
		print(thisTag["name"]+": "+grabTag(html, thisTag["openTag"], thisTag["closeTag"], eliminate))

if __name__ == '__main__':

	p = getCmdLineParser()
	args = p.parse_args()

	cfg = RawConfigParser()
	cfg.read(args.config_file)
	rightNow = time.strftime("%Y%m%d%H%M%S")
	logger = initLog(rightNow)
	logger.info('Starting Run: '+currentDayStr()+'  ==============================')

	with open(args.input_file) as f:
		for line in f:
			scrapeIt(json.loads(line))

    	

	logger.info('Ending Run: '+currentDayStr()+'  ==============================')
