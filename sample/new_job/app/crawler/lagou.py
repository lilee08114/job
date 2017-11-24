import logging
import re
import json
import random
import time 
from io import BytesIO
import gzip
from urllib import request, parse
from urllib.error import URLError, HTTPError
from flask import current_app
from bs4 import BeautifulSoup
from .proxy_ip import GetIps
from ..model import db, User, Jobbrief, Jobdetail, Company, Jobsite, Subscribe

class Crawler_for_Lagou(Format):

	def __init__(self, url, page, keyword, proxy):
		'''on lagou site, the keyword should be posted to its host rather than
		through url

		url: the url that will be visit
		page: which page on that url to visit
		keyword: which keyword's info you want to get
		proxy: 10 proxy ip addresses
		'''
		self.url = url
		self.timeout = 5
		self.proxy_obj = proxy
		rv = True if page==1 else False
		para = {'first':rv, 'pn':page, 'kd':keyword}
		self.data = parse.urlencode(para).encode('utf-8')
		self.header = {'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
					'Connection':'keep-alive',
					'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
					'Cookie':'user_trace_token=20170712112047-fe9dead6591f42f2a63afcfc2b0e07a9; LGUID=20170712112048-1995c8d8-66b1-11e7-a7b9-5254005c3644; index_location_city=%E6%88%90%E9%83%BD; JSESSIONID=ABAAABAACBHABBI4192AB821327D51F91B7440FB1C297B5; _gat=1; PRE_UTM=; PRE_HOST=; PRE_SITE=; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F; _gid=GA1.2.248362695.1509540117; _ga=GA1.2.1509692273.1499829648; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1508330244,1508773823; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1509540129; LGSID=20171101204156-0b7f5844-bf02-11e7-b0f3-525400f775ce; LGRID=20171101204207-124080f9-bf02-11e7-b0f3-525400f775ce; TG-TRACK-CODE=index_search; SEARCH_ID=3f1c510c1d3b4ee98e9329ac74fbf51b',
					'X-Anit-Forge-Code':'0',
					'X-Requested-With':'XMLHttpRequest'}

	def get_proxy(self):
		'''pick a proxy ip randomly from 10 proxy ip addresses
		and construct the header with random User-Agent
		retutn: tuple with proxy opener and header
		'''
		user_agent, proxy = random.choice(self.proxy_obj)
		handler = request.ProxyHandler(proxy)
		opener = request.build_opener(handler)
		header = {'User-Agent':user_agent,
					'Accept-Encoding':'gzip, deflate, br',
					'Referer':'https://www.lagou.com/jobs/list_python?labelWords=&\
								fromSearch=true&suginput=',
					'Host':'www.lagou.com',
					'Origin':'https://www.lagou.com',
					'Accept':'application/json, text/javascript, */*; q=0.01',
					'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'
					}
		
		return (opener, header)

	def open_url(self, site, data=None):
		'''open the given site with the proxy opener and header.
		add HTTPError handling logic here!
		'''
		opener, header = self.get_proxy()
		req = request.Request(site, headers=header)
		try:
			with opener.open(req, data, timeout=self.timeout) as f:
				return f.read().decode('utf-8')
		except HTTPError as e:
			print ('LG HTTPError, %s'%e.code)
			print (site, data)
			#this proxy ip need to be marked in db 
			#self.proxy_obj.remove(temp)
			time.sleep(1)
			return self.open_url(site)
		except URLError:
			print ('URLError! %s'%e.reason)
			time.sleep(1)
			return self.open_url(site)
		except Exception as e:
			print ('Unknown error!, %s'%str(e))
			time.sleep(3)
			return self.open_url(site)
		 

	def job_list(self):
		'''fetch the jon list, and parse and save rough infos about each job.
		return a list containg many dicts, each dict store infos of one job 
		'''
		#jobinfo_without_detail = []

		html = json.loads(self.open_url(self.url, self.data))
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
			if job_already_exist:
				break

		#return jobinfo_without_detail

		

	def job_detail(self, job_link):
		
		time.sleep(2)
		print ('Searching link:',job_link)
		x = gzip.GzipFile(fileobj=BytesIO(self.open_url(job_link)))
		hm = x.read().decode()
		bs = BeautifulSoup(hm, 'html5lib')
		job_requirement = []
		job_labels = []
		for label in bs.find_all(class_='labels'):
			job_labels.append(label.string)
		for requirement in bs.find('dd', class_='job_bt').stripped_strings:
			job_requirement.append(requirement)

		job['job_labels'] = job_labels
		job['job_requirement'] = job_requirement

		return job



