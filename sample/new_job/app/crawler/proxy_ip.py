import re
import sys
import time
from bs4 import BeautifulSoup
from urllib import request
from flask import current_app
from ..model import db, Ip_pool



class GetIps():
	#这个模块作用是接受fresh命令，然后获取20个有效的代理IP，并存储
	def __init__(self):
		#timeout: timeout parameter for urlopen, only for validate_ip method
		self.url1 = 'http://www.xicidaili.com/'
		self.url2 = 'http://www.ip181.com/'
		self.test_url = 'http://www.baidu.com/'
		self.timeout = 5
		self.header={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
			AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
			'Referer':'https://www.google.com/'
			}
		self.ip_pool = []

	def __fetch_ip(self):
		#request the proxy ip addresses, append the validate ip to the ip_pool list
		
		req = request.Request(self.url1, headers=self.header)
		with request.urlopen(req) as f:
			html = f.read().decode()
		bs = BeautifulSoup(html, 'html5lib')
		for i in bs.find_all('tr', class_='subtitle'):
			i.decompose()
		print (len(bs.find_all('tr')))
		for i in bs.find_all('tr'):
			i = str(i)
			ip_addr = re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', i)
			if bool(ip_addr):
				port_ = re.search('<td>(\d{1,5})<\/td>', i)
				security = re.search('高匿|透明', i)
				scheme_ = re.search('(?i)https|http', i)
				ip_obj = (ip_addr.group(), port_.group(1), security.group(), scheme_.group())
				print ('-----------?--------')
				print (ip_obj)
				if self.validate_ip(ip_obj) == True:
					self.ip_pool.append(ip_obj)
					

	def validate_ip(self, ip_obj):
		#visit a test_url to check whether a proxy ip is alive
		ip, port, security, scheme = ip_obj
		if security == '透明':
			return False
		return True
		

	def __save(self):
		#write the ip addresses into db.
		from app.myapp import app
		with app.app_context():
			#db.create_all()
			for i in self.ip_pool:
				ip, port, security, scheme = i
				new_ip = Ip_pool(ip=ip, port=port, security=security, scheme=scheme)
				db.session.add(new_ip)
				try:
					db.session.commit()
				except:
					db.session.rollback()
					
			#save it !

	def fresh_ip(self):
		#exposed api??
		self.__fetch_ip()
		if len(self.ip_pool) > 0:
			self.__save()
			return True
		else:
			print ('---------------------------')
			print ('didn\'t get any useful ip addrs!')
			print ('---------------------------')
			return False
