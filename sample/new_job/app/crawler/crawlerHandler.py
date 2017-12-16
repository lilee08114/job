import logging
import random
from urllib.parse import quote
#约定：发布时间选项为：None, 24  72
#约定：工资有None, ‘3K以下’，‘3k-6k’，‘6k-10k’，‘10k以上’
#约定：经验要求：None,‘无要求’，‘1-3年’，‘3年以上’
#################################################################
#this module is to generate the url base on the given criterion
#such as city, key word, salary and etc.
#different filter condition will lead into different url
#################################################################

class Links():

	def __init__(self, keyword, exp=None, edu=None, page=1,
				city='成都', salary=None, pub_time=None):
		'''this is not fully implemented for now, only keyword must be provided
		
		keyword: string, the keyword that will be searched
		'''
		self.keyword = keyword
		self.exp = exp
		self.edu = edu
		self.city = city
		self.salary = salary
		self.page = page
		self.pub_time = pub_time

	def qianCheng(self):
		'''generate the url for qiancheng website

		reutrn string, a string url
		'''
		if self.city == '成都':
			city_code = '090200'
			area_code = '090200'
		if self.pub_time is None:
			pub_time_code = 9
		elif self.pub_time == '24':
			pub_time_code = 0
		elif self.pub_time == '72':
			pub_time_code = 1
		if self.salary is None:
			salary_code = 99
		keyword_code = quote(self.keyword)
		page_code = self.page
		if self.exp is None:
			exp_code = None
		elif self.exp == '无要求':
			exp_code = '01'
		elif self.exp == '1-3年':
			exp_code = '02'
		elif self.exp == '3年以上':
			exp_code = '03'
		link =  'http://search.51job.com/list/%s,%s,0000,00,%s,%s,%s,2,%s.html?workyear=%s'%(
				city_code, area_code, pub_time_code,salary_code, keyword_code, page_code,
				 exp_code)
		logging.info('Searching QC MAIN: key: %s, link: %s'%(self.keyword, link))
		return link


	def liePin(self):
		'''generate the url for liepin website

		reutrn string, a string url
		'''
		keyword_code = quote(self.keyword)
		if self.city == '成都':
			city_code = 280020
		if self.pub_time is None:
			pub_time_code = None      #quote(pub_time)
		elif self.pub_time == '24':
			pub_time_code = 1
		elif self.pub_time == '72':
			pub_time_code = 3
		if self.salary is None:
			salary_code = None
		page_code = self.page
		link = 'https://www.liepin.com/zhaopin/?key=%s&dqs=%s&pubTime=%s&salary=%s&curPage=%s'%(keyword_code, \
				city_code, pub_time_code, salary_code, page_code)
		logging.info('Searching LP MAIN: key: %s, link: %s'%(self.keyword, link))
		return link

	def laGou(self):
		'''generate the url for lagou website

		reutrn string, a string url
		'''
		city_code = quote(self.city)
		page = self.page
		#keyword = self.keyword
		link = 'https://www.lagou.com/jobs/positionAjax.json?city=%s&needAddtionalResult=false&isSchoolJob=0'%city_code
		logging.info('Searching LG MAIN: key: %s, link: %s'%(self.keyword, link))
		return link

