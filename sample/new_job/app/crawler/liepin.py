import logging
import time
import random
from urllib import request, parse
from urllib.error import URLError, HTTPError
from io import BytesIO
import gzip
from bs4 import BeautifulSoup
from app.model import User, Jobbrief
from . import Format

#####################################
#crawler for liepin.com
#####################################

class Crawler_for_Liepin(Format):
	
	def __init__(self, url, proxy, key):
		'''open the given url, parse the html content, save the job, then open job site and save it

		url: string, the url that will be visited
		key: string, which keyword's info you want to get
		proxy: list, contains 30 proxy ip addresses in dict format
		'''
		self.keyword = key
		self.url = url
		self.timeout = 10
		self.proxy_obj = proxy

	def get_proxy(self):
		'''pick one proxy ips randomly, build the request header, build the proxy opener
		'''
		user_agent, proxy = random.choice(self.proxy_obj)
		header = {'User-Agent':user_agent,
					'Referer':'https://www.liepin.com/zhaopin/',
					'Host':'www.liepin.com',
					'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
					'Accept-Encoding':'gzip, deflate, br',
					'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
					'Referer':'https://www.liepin.com/zhaopin/'
					}
		handler = request.ProxyHandler(proxy)
		opener = request.build_opener(handler)
		return (opener, header)

	def open_url(self, site):
		'''open the given site with the proxy opener and header
		if the response status code is 403, mark it in database and retry with other proxy ip
		'''
		logging.info('[open url]URL is: {}'.format(site))
		opener, header = self.get_proxy()
		req = request.Request(site, headers=header)
		try:
			with opener.open(req, timeout=self.timeout) as f:
				x = gzip.GzipFile(fileobj=BytesIO(f.read()))
			return x.read().decode()
		except HTTPError as e:
				logging.warning('[open url]LP HTTPError %s'%(e.code))
				#this proxy ip need to be marked in db 
				#self.proxy_obj.remove(temp)
				time.sleep(1)
				return self.open_url(site)
		except URLError as e:
			logging.warning('[open url]URLError! %s'%e.reason)
			time.sleep(1)
			return self.open_url(site)
		except Exception as e:
			logging.error('[open url]Unknown error!, %s'%str(e))
			time.sleep(3)
			return self.open_url(site)

	def job_list(self):
		'''get the job list, parse the job-relative info, and save it into db
		'''
		#information = []
		html = self.open_url(self.url)
		bs = BeautifulSoup(html, 'html5lib')		

		for job_tag in bs.find_all('div', class_='sojob-item-main clearfix'):

			job_info = {}
			job_info['job_name'] = str(job_tag.find('a',attrs={'data-promid':True}).string.strip())
			job_info['link'] = str(job_tag.find('a',attrs={'data-promid':True})['href'])
			remuneration = job_tag.find(class_='condition clearfix')['title'].split('_')
			job_info['salary'] = remuneration[0]
			job_info['job_location'] = remuneration[1]
			job_info['edu'] = remuneration[2]
			job_info['exp'] = remuneration[3]
			job_info['pub_time'] = str(job_tag.find('time').string)
			#print (job_tag)
			job_info['company_name'] = str(job_tag.find('p', class_='company-name').find('a').string)
			job_info['company_site'] = job_tag.find('p', class_='company-name').find('a').get('href')

			job_already_exist = self.save_raw_info(job_info)
			if job_already_exist:				# if found a repeated job, stop proceeding
				break
	
	def check_link(self, link):
		'''transfer the link from relative into absolute url'''
		host = 'https://www.liepin.com'
		path = link
		if host in path:
			return path
		else:
			return parse.urljoin(host, path)

	def job_detail(self, job_id, job_link):
		'''open the given job links, save the detail requirments it into db

		job_id: integer, job's database row id
		job_link: job's detail info link
		'''
		job_requirement = []
		url = self.check_link(job_link)
		logging.info('Searching LP DETL: key: ?, link: %s'%(url))

		bs = BeautifulSoup(self.open_url(url), 'html5lib')
		#print (html)
		try:
			result = bs.find(class_='content content-word').strings
		except AttributeError:
			result = bs.find(class_='job-info-content').strings
		except Exception as e:
			result = ['Sorry, failed to fetch the contents, URL is {}'.format(url)]

		for i in result:
			job_requirement.append(str(i))
		requirement = ' '.join(job_requirement)
		self.save_detail_info(job_id, requirement)
	
		job = Jobbrief.query.get(job_id)
		labels = self.extract_labels(requirement)
		job._update(job_labels=', '.join(labels))
		return

		