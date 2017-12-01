import random

from app.model import Ip_pool
from app.proxy import GetIps

class ProxyPool():

	@classmethod
	def _user_agent_resources(cls):
		#user_agent list
		user_agents = ['Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) \
				AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
			'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 \
				(KHTML, like Gecko) Version/5.1 Safari/534.50',
			'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0',
			'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
			'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
			'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
			'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
			'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
			'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11',
			'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
			'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 \
				(KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
			'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)',
			'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)',
			'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
			'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)',
			'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; \
				SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
			'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)',
			'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)',
			'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
			]
		return random.choices(user_agents, k=30)

	@classmethod
	def update_ip(cls):
		print ('--searching the proxy ip--')
		search_proxy = GetIps()
		search_proxy.fresh_ip()
		print ('--searching ends--')

	@classmethod
	def _proxy_resources(cls, site):
		#在这里添加，ip库刷新逻辑
		'''input: 'qc' or 'lg' or 'lp' corresponding to each website
		get 10 proxy ip addresses from database
		return: a list of proxy ip addresses
		'''
		from app import app
		with app.app_context():
			if site == 'qc':
				ip_obj = Ip_pool.query.filter_by(qc_status=True).all()
				print ('----qc-%s-----'%(len(ip_obj)))
				if len(ip_obj) < 30:
					cls.update_ip()
					ip_obj = Ip_pool.query.filter_by(qc_status=True).all()
			elif site == 'lg':
				ip_obj = Ip_pool.query.filter_by(lg_status=True).all()
				print ('----lg-%s-----'%(len(ip_obj)))
				if len(ip_obj) < 30:
					cls.update_ip()
					ip_obj = Ip_pool.query.filter_by(qc_status=True).all()
			elif site == 'lp':
				ip_obj = Ip_pool.query.filter_by(lp_status=True).all()
				print ('----lp-%s-----'%(len(ip_obj)))
				if len(ip_obj) < 30:
					cls.update_ip()
					ip_obj = Ip_pool.query.filter_by(qc_status=True).all()
			else:
				return None

			twenty_ip = random.sample(ip_obj, 30)
			#return [{i.scheme : 'http://'+i.ip+':'+i.port} for i in twenty_ip]
			return [{i.scheme : 'http://'+i.ip+':'+i.port} for i in twenty_ip] #{'http':'http://'}

	@classmethod
	def get_30_proxies(cls, site):
		#input: 'qc' or 'lg' or 'lp' corresponding to each website
		#return 10 proxy addresses, each one was attached with a user_agent
		return list(zip(cls._user_agent_resources(), cls._proxy_resources(site)))
