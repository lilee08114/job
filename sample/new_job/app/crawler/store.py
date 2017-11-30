import logging
from .crawlerHandler import Links
from app import ce
from . import whenFinishCrawlDetail, whenFinishUpdateStatus
from .lagou import Crawler_for_Lagou
from .liepin import Crawler_for_Liepin
from .qiancheng import Crawler_for_51job
from .proxy_pool import ProxyPool

#这个module相互引用太严重，是很脆弱的，最好能切分开

#根据视图传来的URL和PROXY， 调用crawler的list，结束后从数据库搜寻site，进行详情抓取


class Crawler():

	def __init__(self, key_word)
		self.key_word = key_word
		self.proxy = ProxyPool.get_30_proxies('qc')
		link = Links(key_word)
		#self.qc_link = link.qianCheng()
		#self.lp_link = link.liePin()
		#self.lg_link = link.laGou()
		self.qc = Crawler_for_51job(link.qianCheng(), self.proxy)
		self.lp = Crawler_for_Liepin(link.liePin(), self.proxy)
		self.lg = Crawler_for_Lagou(link.laGou(), self.proxy)



	def Start(self, subscribe=False):
		pass


	@ce.task(base=whenFinishCrawlDetail)
	def qc_list(self, subscribe, identifier='qc'):
		#qc = Crawler_for_51job(self.qc_link, self.proxy)
		self.qc.job_list()

	@ce.task(base=whenFinishCrawlDetail)
	def lp_list(self, subscribe, identifier='lp'):
		#lp = Crawler_for_Liepin(self.lp_link, self.proxy)
		self.lp.job_list()

	@ce.task(base=whenFinishCrawlDetail)
	def lg_list(self, subscribe, identifier='lg'):
		#lg = Crawler_for_Lagou(self.lp_link, self.proxy)
		self.lg.job_list()

	@ce.task(base=whenFinishUpdateStatus)
	def qc_detail(self, job_id, job_link):
		self.qc.job_detail(job_id, job_link)

	@ce.task(base=whenFinishUpdateStatus)
	def lp_detail(self, job_id, job_link):
		self.lp.job_detail(job_id, job_link)

	@ce.task(base=whenFinishUpdateStatus)
	def lg_detail(self, job_id, job_link):
		self.lg.job_detail(job_id, job_link)




