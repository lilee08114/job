import re
import logging
import time
import random
from urllib import request, parse
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup
from app.model import User, Jobbrief
from . import Format


class Crawler_for_51job(Format):
	
	def __init__(self, url, proxy, key):
		self.keyword = key
		self.proxy_obj = proxy
		self.agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
		self.ref = 'http://search.51job.com/list/090200,090200,0000,9,9,99,python,2,1.html?'		
		self.url = url
		self.timeout = 5
		'''
		self.header = {'User-Agent':self.agent, 
					   'Referer':self.ref,
					   'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
					   'Cache-Control':'max-age=0',
					   'Connection':'keep-alive',
					   'Host':'jobs.51job.com'
					    }
		#self.request = urllib.request(self.url, None,self.header)
		'''
	def get_proxy(self):
		user_agent, proxy = random.choice(self.proxy_obj)
		header = {'User-Agent':user_agent,
						'Referer':self.ref,
						'Host':'jobs.51job.com'
						}
		handler = request.ProxyHandler(proxy)
		opener = request.build_opener(handler)
		return (opener, header)

	def open_url(self, site):
		opener, header = self.get_proxy()
		req = request.Request(site, headers=header)
		try:
			with opener.open(req, timeout=self.timeout) as f:
				return f.read()
		except HTTPError as e:
			print ('QC HTTPError, %s'%e.code)
			#this proxy ip need to be marked in db 
			#self.proxy_obj.remove(temp)
			time.sleep(1)
			return self.open_url(site)
		except URLError as e:
			print ('URLError!, %s'%e.reason)
			time.sleep(1)
			return self.open_url(site)
		except Exception as e:
			print ('Unknown error!, %s'%str(e))
			time.sleep(3)
			return self.open_url(site)

	def job_list(self):
		html = self.open_url(self.url)
		bs = BeautifulSoup(html, 'html5lib')

		job_list = []
		et = bs.find(class_="el title")
		if et:
			et.decompose()
		for job_obj in bs.find(attrs={'id':'resultList'}).find_all(class_='el'):
			single_job_info = {}
			single_job_info['job_name'] = job_obj.find_all('a')[0].string.strip()
			single_job_info['link'] = job_obj.find_all('a')[0]['href']
			single_job_info['company_name'] = str(job_obj.find_all('a')[1].string)
			single_job_info['company_site'] = job_obj.find_all('a')[1]['href']
			single_job_info['salary'] = str(job_obj.find(class_='t4').string)
			single_job_info['job_location'] = str(job_obj.find(class_='t3').string)
			single_job_info['pub_time'] = str(job_obj.find(class_='t5').string)
			#job_list.append(single_job_info)
			job_already_exist = self.save_raw_info(single_job_info)
			if job_already_exist:
				break
		#return job_list


	def job_detail(self, job_id, job_link):
		''' return a list consisting many dicts that contain 
			the job information(e.g: salary, experience request, 
			work location etc.) ,and will pause for seconds between 
			each pages in case too frequent requests will alert 
			the web manager.
		'''
		#time.sleep(3)
		#logging.info('Searching QC DETL: key: %s, link: %s'%(jobInfo['key'], jobInfo['link']))
		html = self.open_url(job_link)
		#print (html)
		bs = BeautifulSoup(html, 'html5lib')
			
		exp = str(bs.find(class_='i1').next_sibling) if bs.find(class_='i1') else None
		edu = str(bs.find(class_='i2').next_sibling)	if bs.find(class_='i2') else None
		quantity = str(bs.find(class_='i3').next_sibling) if bs.find(class_='i3') else None
		other_requirement = str(bs.find(class_='i5').next_sibling) if \
										bs.find(class_='i5') else None

		job_description = []
		for tag in bs.find(class_="bmsg job_msg inbox").find_all('a'):
			tag.decompose()
		for info in bs.find(class_="bmsg job_msg inbox").stripped_strings:
			job_description.append(info)
		jobInfo['job_requirement'] = job_description

		requirement = ', '.join(job_description)
		self.save_detail_info(job_id, requirement)

		labels = self.extract_labels(requirement)
		job = Jobbrief.query.get(job_id)
		job._update(job_labels=', '.join(labels),
					job_exp=self.exp_format(exp), 
					job_edu=edu, 
					job_quantity=quantity,
					job_other_require=other_requirement
					)

		return jobInfo



