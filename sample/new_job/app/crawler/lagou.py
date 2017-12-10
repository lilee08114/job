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

class Crawler_for_Lagou(Format):

	def __init__(self, url, proxy, keyword, page=1):
		'''on lagou site, the keyword should be posted to its host rather than
		through url

		url: the url that will be visit
		page: which page on that url to visit
		keyword: which keyword's info you want to get
		proxy: 10 proxy ip addresses
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
		print ('URL is: {}, and set trace now'.format(site))
		#pdb.set_trace()
		try:
			print ('-------------head start-----------')
			print (opener.open(req, data, timeout=self.timeout).info())
			print ('-------------head end-----------')
			with opener.open(req, data, timeout=self.timeout) as f:
				return f.read()
		
		except HTTPError as e:
			print ('LG HTTPError, %s, e %s'%(e.code, e))
			#print ('LG site is {}, and UA is {}'.format(site, header['User-Agent']))
			#f = opener.open(req, data, timeout=self.timeout)
			print ('-------------head start-----------')
			#print (f.info())
			print ('-------------head end-----------')
			#this proxy ip need to be marked in db 
			#self.proxy_obj.remove(temp)
			time.sleep(1)
			#return self.open_url(site)
		except URLError as e:
			print ('URLError! %s'%e.reason)
			time.sleep(1)
			#return self.open_url(site)
		except Exception as e:
			print ('Unknown error!, %s'%str(e))
			time.sleep(3)

			#return self.open_url(site)


	def job_list(self):
		'''fetch the jon list, and parse and save rough infos about each job.
		return a list containg many dicts, each dict store infos of one job 
		'''
		#jobinfo_without_detail = []

		html = json.loads(self.open_url(self.url, self.data).decode('utf-8'))
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

		

	def job_detail(self, job_id, job_link):
	
		x = gzip.GzipFile(fileobj=BytesIO(self.open_url(job_link)))
		html = x.read().decode()
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



