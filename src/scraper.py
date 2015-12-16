#!/usr/bin/env python

from __future__ import print_function      # get latest print functionality

from bs4 import BeautifulSoup
import urllib2
import re
import logging
import sys
import time               # sleep function for connection back-off
import json               # JSON object encoding/decoding
from random import randint
from time import sleep

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


def grabTag2(soup, openTag, closeTag, eliminate):
	if closeTag is Null:
		if openTag=="<title>":
			return soup.title.string



def grabTag(html, openTag, closeTag, eliminate):

	result=re.search(openTag+'(.*)'+closeTag, html)

	if hasattr(result, 'group'):
		try:
			s = result.group(1).replace(eliminate,"")
		except:
			s = "utf issue. fix this"	 
		return s
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

def sendToOutput(destination, vals):
	if vals is not None:
		line=vals["url"]+"| "+json.dumps(vals)
		print(line, file=destination)

def scrapeIt(scrapeObj):
	retval = {}
	retval["url"]=scrapeObj["url"]

	opener = urllib2.build_opener()
	opener.addheaders = [('User-agent', 'Mozilla/5.0')]
	try:
		response = opener.open(scrapeObj["url"])
		html = response.read()
		soupObj = BeautifulSoup(html, "html.parser")
		for thisTag in scrapeObj["get"]:
			eliminate=""
			if "eliminate" in thisTag:
				eliminate=thisTag["eliminate"]
			if "openTag" in thisTag and "closeTag" in thisTag:
				retval[thisTag["name"]]=grabTag(html, thisTag["openTag"], thisTag["closeTag"], eliminate)
			elif "tag" in thisTag:
				retval[thisTag["name"]]=grabTag2(soup, thisTag["Tag"], None, eliminate)
	except: 
		logger.info("HTTP Exception: "+scrapeObj["url"])
		return None
	return retval

if __name__ == '__main__':

	p = getCmdLineParser()
	args = p.parse_args()

	cfg = RawConfigParser()
	cfg.read(args.config_file)
	rightNow = time.strftime("%Y%m%d%H%M%S")
	logger = initLog(rightNow)
	logger.info('Starting Run: '+currentDayStr()+'  ==============================')
	x = 1
	outFile = open(args.output_file,'w')
	with open(args.input_file) as f:
		for line in f:
			sleep(randint(2,10))
			logger.info("Processing Record: "+str(x))
			vals = scrapeIt(json.loads(line))
			sendToOutput(outFile, vals)
			x=x+1
	outFile.close()
    	

	logger.info('Ending Run: '+currentDayStr()+'  ==============================')
