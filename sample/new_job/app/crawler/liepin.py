import logging
import time
import random
from urllib import request, parse
from urllib.error import URLError, HTTPError
from io import BytesIO
import gzip
from bs4 import BeautifulSoup
from ..model import User, Jobbrief


class Crawler_for_Liepin(Format):
	
	def __init__(self, url, proxy):
		self.url = url
		self.timeout = 5
		self.proxy_obj = proxy
		'''
		self.header = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
						'Accept-Encoding':'gzip, deflate, br',
						'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
						'Cache-Control':'max-age=0',
						'Connection':'keep-alive',
						'Cookie':'gr_user_id=6b586e66-717d-4278-a73f-faa25825b1d1; __uuid=1501212420310.14; _uuid=873BADACFFA8440C4C60DB89EE03D36A; _fecdn_=1; slide_guide_home=1; JSESSIONID=78D969B17C23427D97202447C1E90DE4; abtest=0; __tlog=1503294086561.02%7C00000000%7CR000000075%7C00000000%7C00000000; __session_seq=16; __uv_seq=13; Hm_lvt_a2647413544f5a04f00da7eee0d5e200=1501212421,1501908343,1503294087; Hm_lpvt_a2647413544f5a04f00da7eee0d5e200=1503367763; _mscid=00000000; gr_session_id_bad1b2d9162fab1f80dde1897f7a2972=a0b1a522-6d65-4eb6-ae07-12e291d7878a',
						'Host':'www.liepin.com',
						'Referer':'https://www.liepin.com/zhaopin/',
						'Upgrade-Insecure-Requests':1,
						'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'
						}
		'''
	def get_proxy(self):
		'''pick a proxy ip randomly from 10 proxy ip addresses
		and construct the header with random User-Agent
		retutn: tuple with proxy opener and header
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
		print ('---open: %s-----'%site)
		opener, header = self.get_proxy()
		req = request.Request(site, headers=header)
		try:
			with opener.open(req, timeout=self.timeout) as f:
				x = gzip.GzipFile(fileobj=BytesIO(f.read()))
			return x.read().decode()
		except HTTPError as e:
				print ('LP HTTPError %s'%(e.code))
				#this proxy ip need to be marked in db 
				#self.proxy_obj.remove(temp)
				time.sleep(1)
				return self.open_url(site)
		except URLError as e:
			print ('URLError! %s'%e.reason)
			time.sleep(1)
			return self.open_url(site)
		except Exception as e:
			print ('Unknown error!, %s'%str(e))
			time.sleep(3)
			return self.open_url(site)

	def job_list(self):
		'''get the job list, parse the job-relative info, and save it into db

		return a list that including many dicts, each dicts stores a job's rough info
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
			
			#job_info['company_site'] = job_tag.find('p', class_='company-name').find('a')['href']
			#information.append(job_info)
			job_already_exist = self.save_raw_info(job_info)
			if job_already_exist:
				break

		#print ('Liepin\'s search page has been parsed')
		#return information
	
	def check_link(self, link):
		#check the validity of the link
		host = 'https://www.liepin.com'
		path = link
		if host in path:
			return path
		else:
			return parse.urljoin(host, path)

	def job_detail(self, job_id, job_link):
		'''base on the given job links, save the detail requirments it into db

		param:
		job_id: job's raw info id
		job_link: job's detail info link
		'''
		job_requirement = []
		url = self.check_link(job_link)
		logging.info('Searching LP DETL: key: %s, link: %s'%(job['key'], url))

		bs = BeautifulSoup(self.open_url(url), 'html5lib')
		#print (html)
		try:
			result = bs.find(class_='content content-word').strings
		except AttributeError:
			result = bs.find(class_='job-info-content').strings
		except Exception, e:
			result = ['Sorry, failed to fetch the contents, URL is {}'.format(url)]

		for i in result:
			job_requirement.append(str(i))
		requirement = ' '.join(job_requirement)
		self.save_detail_info(job_id, requirement)
	
		job = Jobbrief.query.get(job_id)
		labels = self.extract_labels(requirement)
		job._update(job_labels=', '.join(labels))
		return job
'''
url = 'https://www.liepin.com/zhaopin?pubTime=3&dqs=280020&salary=10$15&compscale=&key=Python'
outurl = r'C:\works\crawler\liepin.txt'
a = Crawler_for_Liepin(url)
print (a)
print ('start:...')
p = str(a.jobDetail())	
with open(outurl, 'a', encoding='utf-8', errors='ignore') as c:
	c.write(p) 	
print ('end!')
'''
		