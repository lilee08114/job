import re
import logging
from bs4 import BeautifulSoup
from urllib import request
from flask import current_app
from app.model import Ip_pool
from app.extensions import db
from app.extensions import ce

class GetIps():
	#这个模块作用是接受fresh命令，get ip proxy from website!
	def __init__(self):
		#timeout: timeout parameter for urlopen, only for validate_ip method
		self.url1 = 'http://www.xicidaili.com/'
		self.url2 = 'http://www.ip181.com/'
		self.url3 = ' http://www.data5u.com/'
		self.url4 = 'http://www.66ip.cn/'
		self.url6 = 'http://www.goubanjia.com/free/gngn/index.shtml'
		self.url7 = 'http://www.xdaili.cn/ipagent/freeip/getFreeIps?page=1&rows=10'
		self.test_url = 'http://www.baidu.com/'
		self.timeout = 10
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

	def save(self):
		#write the ip addresses into db.
		from app import app
		with app.app_context():
			#db.create_all()
			for i in self.ip_pool:
				ip, port, security, scheme = i
				new_ip = Ip_pool(ip=ip, port=port, security=security, scheme=scheme)
				new_ip._save()



	def _parse_tr_tag(self, tr_tag):
		ip_addr = re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', tr_tag)
		if bool(ip_addr):
			port_ = re.search('<td>(\d{1,5})<\/td>', tr_tag)
			security = re.search('高匿|透明|普匿', tr_tag)
			scheme_ = re.search('(?i)https|http', tr_tag)
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
			
			if ip_obj and self._validate_ip(ip_obj) == True:
				self.ip_pool.append(ip_obj)
		self.save()

	def _ip181_ip(self):
		html = self._open_url(self.url2)
		bs = BeautifulSoup(html, 'html5lib')

		for tag in bs.find_all('tr')[2:]:
			if 'more' in str(tag):
				continue
			if 'subtitle' in str(tag):
				continue
			if 'active' in str(tag):
				continue
			ip_obj = self._parse_tr_tag(str(tag))
			if self._validate_ip(ip_obj) == True:
				self.ip_pool.append(ip_obj)
		self.save()
		
	@ce.task(queue='check')
	def _check(self, proxy_obj):
		#pk: proxy pk in database
		#proxy_ip: proxy like 'http://117.65.35.123:55555'.
		proxy = {'http://':proxy_obj.scheme+proxy_obj.ip+':'+proxy_obj.port}
		handler = request.ProxyHandler(proxy)
		opener = request.build_opener(handler)
		req = request.Request(self.test_url, headers=self.header, method='HEAD')
		try:
			print (opener.open(req, timeout=self.timeout).getcode())
		except HTTPError as e:
			logging.warning('[confirm proxy]HTTPError, %s'%e.code)
			proxy_obj._delete()
		except URLError as e:
			logging.warning('[confirm proxy]URLError, %s'%e.reason)
			proxy_obj._delete()
		except Exception as e:
			logging.error('[confirm proxy]bad request! %s'%str(e))
			#return False

	def check(self):
		#这里可以添加更多的筛选条件
		proxies = Ip_pool.query.all()
		for proxy in proxies:
			#self._check.apply_async((proxy,))
			GetIps._check.apply_async((self, proxy))
			#break

	def fresh_ip(self, check=True):
		#exposed api??
		#here need more proxy searching logic
		self._xicidaili_ip()
		self._ip181_ip()
		if check:
			self.check()
			

