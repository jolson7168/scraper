from ConfigParser import RawConfigParser

import requests
import cookielib
import json

def getCmdLineParser():
    import argparse
    desc = 'Execute scrape report demo'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-c', '--config_file', default='../config/reportscrape_config',
                        help='configuration file name (*.ini format)')

    return parser



if __name__ == '__main__':

	p = getCmdLineParser()
	args = p.parse_args()

	cfg = RawConfigParser()
	cfg.read(args.config_file)

	list1=json.loads(cfg.get('scrape', 'data'))
	targets=[]
	for i in xrange(0,len(list1),2):
		x={}
		x["source"]=list1[i]
		x["target"]=list1[i+1]
		targets.append(x)


	authHeaders = {
			"DNT":1, 
			"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
			"Accept-Encoding":"gzip, deflate",
			"Accept-Language":"en-US,en;q=0.5",
			"Connection":"keep-alive",
			"Cookie":"ServerID=1110",
			"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0",
			"Referer":cfg.get('scrape', 'referer'),
			"Host":cfg.get('scrape', 'host')
		   }



	payload = {"SourcePage": "/","ID": "none","redirectToHttps":"ignore","un":cfg.get('scrape', 'login'),"pw":cfg.get('scrape', 'password'),"submit":"Log In"}

			
	s = requests.Session()
	r = s.post(cfg.get('scrape', 'url'), headers = authHeaders, data = payload)

	c2 = requests.utils.dict_from_cookiejar(s.cookies)

	reportHeaders = {
			"DNT":1, 
			"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
			"Accept-Encoding":"gzip, deflate",
			"Accept-Language":"en-US,en;q=0.5",
			"Connection":"keep-alive",
			"Cookie":"ServerID=1110; .IDSDR="+c2[".IDSDR"],
			"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0",
			"Host":cfg.get('scrape', 'host')
		   }

	for doc in targets:
		with open(doc["target"], 'wb') as handle:
			response = s.get(doc["source"], headers = reportHeaders, stream = True)
			if not response.ok:
				print(response)
			for block in response.iter_content(1024):
				handle.write(block)





