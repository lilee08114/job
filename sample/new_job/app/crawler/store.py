import logging
from datetime import datetime
from celery import Task
from .crawlerHandler import Links
from app import ce
from .lagou import Crawler_for_Lagou
from .liepin import Crawler_for_Liepin
from .qiancheng import Crawler_for_51job
from .proxy_pool import ProxyPool
from app.model import User, Jobbrief, Jobdetail, Company, Jobsite, Subscribe

#这个module相互引用太严重，是很脆弱的，最好能切分开

#根据视图传来的URL和PROXY， 调用crawler的list，结束后从数据库搜寻site，进行详情抓取


class whenFinishCrawlDetail(Task):

	def links_filter(self, identifier):
		#[(1,'www....', (2,'wwww....'))]
		#获取每个工作的link和id，不使用外键
		links = []
		for job in Jobsite.query.filter_by(have_detail=False).all():
			if identifier == 'lp':
				if 'liepin' in job.site or 'www' not in job.site:
					links.append((job.brief_id, job.site))
			elif identifier == 'qc':
				if '51job' in job.site:
					links.append((job.brief_id, job.site))
			elif identifier == 'lg':
				if 'lagou' in job.site:
					links.append((job.brief_id, job.site))
		return links

	def on_success(self, retval, task_id, args, kwargs):
		#从数据库里拿出have_detail为False的数据，筛选，启动相应的详情抓取爬虫 
		#根据identifier来决定从数据库刷选那些网站的链接来进行详情抓取
		identifier = args[2]
		links = self.links_filter(identifier)
		ins = args[0]  #???
		is_subscribe = args[1]
		print ('----------ON SUCCESS START----------')
		print ('identifier: {}, links:{}, ins:{}, is_subscribe:{}'.\
			format(identifier, links, ins, is_subscribe))
		print ('----------ON SUCCESS END----------')
		for link in links:
			if identifier == 'qc':
				Crawler.qc_detail.apply_async((ins, link[0], link[1], is_subscribe))
			elif identifier == 'lp':
				Crawler.lp_detail.apply_async((ins, link[0], link[1], is_subscribe))
			elif identifier == 'lg':
				Crawler.lg_detail.apply_async((ins, link[0], link[1], is_subscribe))
		
class whenFinishUpdateStatus(Task):

	def on_success(self, retval, task_id, args, kwargs):
		ins = args[0]
		brief_id = args[1]
		
		job_link = Jobsite.query.filter_by(brief_id=brief_id).first()
		if job_link:
			job_link._update(have_detail=True)
		#根据subscribe来决定是否写入subcribe数据库记录
		is_subscribe = args[3]
		if is_subscribe:
			key_word = ins.key_word
			subscribe = Subscribe.query.filter_by(sub_key=key_word).first()
			if subscribe:
				subscribe._update(sub_end=datetime.now())


class Crawler():

	def __init__(self, key_word):
		self.key_word = key_word
		self.proxy = ProxyPool.get_30_proxies('qc')
		link = Links(key_word)
		#self.qc_link = link.qianCheng()
		#self.lp_link = link.liePin()
		#self.lg_link = link.laGou()
		self.qc = Crawler_for_51job(link.qianCheng(), self.proxy, key_word)
		self.lp = Crawler_for_Liepin(link.liePin(), self.proxy, key_word)
		self.lg = Crawler_for_Lagou(link.laGou(), self.proxy, key_word)


	def subsequent_tasks(self, days, interval):
		#根据间隔的天数获取任务的countdown数列，据此生成后续的所有任务对象
		#以list形式返回
		ct = []
		ct_time = interval
		while ct_time < days*24*60*60:
			ct.append(ct_time)
			ct_time += interval
			
		subsequent_qc = [Crawler.qc_list.apply_async((self, True), countdown=i) for i in ct]
		subsequent_lp = [Crawler.lp_list.apply_async((self, True,), countdown=i) for i in ct]
		subsequent_lg = [Crawler.lg_list.apply_async((self, True,), countdown=i) for i in ct]
		return (subsequent_qc, subsequent_lp, subsequent_lg)

	def Start(self, subscribe=False, days=3, interval=5*60*60):
		#link决定是否有后续的任务
		#如果有subscribe，则有link任务，link任务中带有countdown参数
		#z这里的subscribe主要是决定在详情抓取任务完成后是否更新subscirbe数据库信息
		subseq_qc = subseq_lp = subseq_lg = None
		if subscribe:
			subseq_qc, subseq_lp, subseq_lg = self.subsequent_tasks(days, interval)

		#Crawler.qc_list.apply_async((self, subscribe, 'qc'), link=subseq_qc)
		#Crawler.lp_list.apply_async((self, subscribe, 'lp'), link=subseq_lp)
		Crawler.lg_list.apply_async((self, subscribe, 'lg'), link=subseq_lg)

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
	def qc_detail(self, job_id, job_link, subscribe):
		self.qc.job_detail(job_id, job_link)

	@ce.task(base=whenFinishUpdateStatus)
	def lp_detail(self, job_id, job_link, subscribe):
		self.lp.job_detail(job_id, job_link)

	@ce.task(base=whenFinishUpdateStatus)
	def lg_detail(self, job_id, job_link, subscribe):
		self.lg.job_detail(job_id, job_link)



