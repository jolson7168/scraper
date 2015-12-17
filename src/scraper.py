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


def grabTag2(soup, openTag, closeTag, eliminate=None):
	if closeTag is Null:
		if openTag=="<title>":
			return soup.title.string



def grabTag(html, openTag, closeTag, eliminate=None):
	result=re.search(openTag+'(.*)'+closeTag, html)
	if hasattr(result, 'group'):
		try:
			if eliminate == None:
				s = result.group(1)
			else:
				s = result.group(1).replace(eliminate,"")
		except:
			s = "utf issue. fix this"	 
		return s
	else:
		return "None"

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
    parser.add_argument('-t', '--test_file', help='html file for testing name')
    parser.add_argument('-s', '--save_html', help='save html file')

    return parser

def sendToOutput(destination, vals):
	if vals is not None:
		line=vals["url"]+"| "+json.dumps(vals)
		print(line, file=destination)

def findBetween( s, first, last ):
	str1= s.decode('utf-8', 'ignore')
	try:
		start = str1.index( first ) + len( first )
		end = str1.index( last, start )
		return str1[start:end]
	except ValueError:
		return ""

def getBetween(html, openTag, closeTag, eliminate):
	retval = findBetween(html, openTag, closeTag)
	if len(retval) == 0:
		retval = "None"
	return retval

def saveIt(directory, url, html):
	end=url[url.rfind("/")+1:]
	fname=directory+"/"+end+".html"
	text_file = open(fname, "w")
	text_file.write(html)
	text_file.close()	
	
def scrapeIt(scrapeObj, html = None, testFilePath = None, saveDirectory = None):
	retval = {}
	opener = urllib2.build_opener()
	opener.addheaders = [('User-agent', 'Mozilla/5.0')]
	try:
		if html == None:
			response = opener.open(scrapeObj["url"])
			html = response.read()
			if saveDirectory is not None:
				saveIt(saveDirectory, scrapeObj["url"], html)
			retval["url"]=scrapeObj["url"]
		else:
			retval["url"]=testFilePath
		soupObj = BeautifulSoup(html, "html.parser")
		for thisTag in scrapeObj["get"]:
			eliminate=None
			if "eliminate" in thisTag:
				eliminate=thisTag["eliminate"]
			if "method" in thisTag:
				if thisTag["method"] == "regexp":
					retval[thisTag["name"]]=grabTag(html, thisTag["openTag"], thisTag["closeTag"], eliminate)
				elif thisTag["method"] == "tag":
					retval[thisTag["name"]]=grabTag2(soup, thisTag["Tag"], None, eliminate)
				elif thisTag["method"] == "instr":
					retval[thisTag["name"]]=getBetween(html, thisTag["openTag"], thisTag["closeTag"], eliminate)

	except: 
		logger.info("HTTP Exception: "+scrapeObj["url"])
		return None
	return retval

def readTest(fname):
	with open(fname) as f:
		data=f.read()
	f.close()
	return data

if __name__ == '__main__':

	p = getCmdLineParser()
	args = p.parse_args()

	cfg = RawConfigParser()
	cfg.read(args.config_file)
	rightNow = time.strftime("%Y%m%d%H%M%S")
	logger = initLog(rightNow)
	logger.info('Starting Run: '+currentDayStr()+'  ==============================')
	x = 1
	html = None
	fname = None
	if args.test_file:
		fname = args.test_file
		html = readTest(args.test_file)
	outFile = open(args.output_file,'w')
	with open(args.input_file) as f:
		for line in f:
			if html is None:
				sleep(randint(2,10))
			logger.info("Processing Record: "+str(x))
			vals = scrapeIt(json.loads(line), html, fname, args.save_html)
			sendToOutput(outFile, vals)
			x=x+1
	outFile.close()
   	

	logger.info('Ending Run: '+currentDayStr()+'  ==============================')
