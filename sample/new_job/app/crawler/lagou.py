import logging
import json
import pdb
import random
import time 
import gzip
from io import BytesIO
from urllib import request, parse
from urllib.error import URLError, HTTPError
from flask import current_app
from bs4 import BeautifulSoup
from app.model import  User, Jobbrief
from . import Format

#####################################
#crawler for lagou.com
#####################################

class Crawler_for_Lagou(Format):

	def __init__(self, url, proxy, keyword, page=1):
		'''open the url, parse the html content, save the job, then open job site and save it

		url: string, the url that will be visited
		page: integer, which page on that url to visit,default to 1
		keyword: string, which keyword's info you want to get
		proxy: list, contains 30 proxy ip addresses in dict format
		'''
		self.keyword = keyword
		self.url = url
		self.timeout = 10
		self.proxy_obj = proxy
		rv = True if page==1 else False
		para = {'first':rv, 'pn':page, 'kd':keyword}
		self.data = parse.urlencode(para).encode('utf-8')
		'''
		self.header = {'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
					'Connection':'keep-alive',
					'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
					'X-Anit-Forge-Code':'0',
					'X-Requested-With':'XMLHttpRequest'}
		'''

	def get_proxy(self):
		'''pick one proxy ips randomly, build the request header, build the proxy opener
		'''
		user_agent, proxy = random.choice(self.proxy_obj)
		handler = request.ProxyHandler(proxy)
		opener = request.build_opener(handler)
		header = {'User-Agent':user_agent,
					'Accept-Encoding':'gzip, deflate, br',
				'Referer':'https://www.lagou.com/jobs/list_python?px=default&city=%E6%88%90%E9%83%BD',
				'Host':'www.lagou.com',
				'Origin':'https://www.lagou.com',
				'Accept':'application/json, text/javascript, */*; q=0.01',
				'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
				'X-Requested-With':'XMLHttpRequest'
					}
		return (opener, header, proxy)

	def _switch_scheme(self, proxy):
		'''switch the proxy ip scheme between 'http' and 'https' '''
		for k, v in proxy.items():
			new_k = 'https' if k=='http' else 'http'
		proxy[new_k] = v
		del proxy[k]
		return proxy

	def _update_proxies(self, origin_proxy):
		'''swith the given origin_proxy's scheme'''
		for i in enumerate(self.proxy_obj):
			k, v = i
			header, proxy = v
			if origin_proxy == proxy:
				new_proxy = self._switch_scheme(origin_proxy)
				self.proxy_obj[k] = (header, new_proxy)

	def open_url(self, site, data=None):
		'''open the given url with proxy opener, if fail, keep retrying'''

		count = 3				#if fails to open the url, just retry 3 times, not infinitely
		opener, header, proxy = self.get_proxy()
		req = request.Request(site, data, headers=header)
		logging.info('[open url]URL is: {}'.format(site))
		#pdb.set_trace()
		try:
			with opener.open(req, timeout=self.timeout) as f:
				html = f.read()
			return (html, proxy)
		
		except HTTPError as e:
			logging.warning('[open url]LG HTTPError, %s, e %s'%(e.code, e))
			count -= 1
			return self.open_url(site)
		except URLError as e:
			logging.warning('[open url]URLError! %s'%e.reason)
			time.sleep(1)
			count -= 1
			self._update_proxies(proxy)
			return self.open_url(site)
		except Exception as e:
			logging.error('[open url]Unknown error!, %s'%str(e))
			time.sleep(3)
			return self.open_url(site)


	def job_list(self):
		'''get the html content, extract and save job information
		'''
		#jobinfo_without_detail = []
		html, proxy = self.open_url(self.url, self.data)
		html = json.loads(html.decode('utf-8'))

		for i in range(4):
			if not html.get('content'):
				time.sleep(2)
				print ('in the while loop')
				self._update_proxies(proxy)
				html, proxy = self.open_url(self.url, self.data)
				html = json.loads(html.decode('utf-8'))
			else:
				break

		for job_json in html['content']["positionResult"]["result"]:
			single_job_info = {}
			single_job_info['pub_time'] = job_json.get("createTime")
			single_job_info['job_name'] = job_json.get("positionName")
			single_job_info['company_site'] = 'https://www.lagou.com/gongsi/%s.ht\
										ml'%(job_json.get("companyId"))
			single_job_info['link'] = 'https://www.lagou.com/jobs/%s.html'%(job_json.get("positionId"))
			single_job_info['edu'] = job_json.get("education")
			single_job_info['salary'] = job_json.get("salary")
			single_job_info['exp'] = job_json.get("workYear")
			single_job_info['company_name'] = job_json.get("companyFullName")
	
			#jobinfo_without_detail.append(single_job_info)
			job_already_exist = self.save_raw_info(single_job_info)
			if job_already_exist:					#if found a repeated job, stop proceeding
				break
		#return jobinfo_without_detail

	def job_detail(self, job_id, job_link):
		'''open the given job_link, extract and save the job's detail
		
		job_id: integer, the job's database raw id
		job_link: string
		 '''
		html, proxy = self.open_url(job_link)
		x = gzip.GzipFile(fileobj=BytesIO(html))
		html = x.read().decode()
		#print (html)
		bs = BeautifulSoup(html, 'html5lib')
		job_requirement = []
		job_labels = []
		for label in bs.find_all(class_='labels'):
			job_labels.append(label.string)
		for requirement in bs.find('dd', class_='job_bt').stripped_strings:
			job_requirement.append(requirement)

		requirement = ' '.join(job_requirement)
		self.save_detail_info(job_id, requirement)
		job = Jobbrief.query.get(job_id)
		job._update(job_labels=', '.join(job_labels))

		return



