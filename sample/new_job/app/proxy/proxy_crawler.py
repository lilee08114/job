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
		self.url3 = ' http://www.data5u.com/'
		self.url4 = 'http://www.66ip.cn/'
		self.url6 = 'http://www.goubanjia.com/free/gngn/index.shtml'
		self.url7 = 'http://www.xdaili.cn/ipagent/freeip/getFreeIps?page=1&rows=10'
		self.test_url = 'http://www.baidu.com/'
		self.timeout = 5
		self.header={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
			AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
			'Referer':'https://www.google.com/'
			}
		self.ip_pool = []

	def _open_url(self, url):
		req = request.Request(self.url1, headers=self.header)
		with request.urlopen(req) as f:
			try:
				html = f.read().decode()
			except UnicodeDecodeError:
				html = f.read().decode('gb2312')
		return html

	def _validate_ip(self, ip_obj):
		#visit a test_url to check whether a proxy ip is alive
		ip, port, security, scheme = ip_obj
		if security == '透明':
			return False
		return True

	def _save(self):
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

	def _parse_tr_tag(self, tr_tag):
		ip_addr = re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', i)
		if bool(ip_addr):
			port_ = re.search('<td>(\d{1,5})<\/td>', i)
			security = re.search('高匿|透明|普匿', i)
			scheme_ = re.search('(?i)https|http', i)
			ip_obj = (ip_addr.group(), port_.group(1), security.group(), scheme_.group())
			return ip_obj


	def _xicidaili_ip(self):
		#get ip from xicidaili.com!	
		html = self._open_url(self.url1)
		bs = BeautifulSoup(html, 'html5lib')
		for i in bs.find_all('tr', class_='subtitle'):
			i.decompose()

		for tag in bs.find_all('tr'):
			ip_obj = self._parse_tr_tag(str(tag))
			print ('-----------?--------')
			print (ip_obj)
			if ip_obj and self._validate_ip(ip_obj) == True:
				self.ip_pool.append(ip_obj)
		self._save()

	def _ip181_ip(self):
		html = self._open_url(self.url2)
		bs = BeautifulSoup(html, 'html5lib')
		title = bs.find(class_='active')
		if title:
			title.decompose()

		for tag in bs.find_all('tr'):
			ip_obj = self._parse_tr_tag(str(tag))
			if self._validate_ip(ip_obj) == True:
				self.ip_pool.append(ip_obj)
		self._save()
					


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
