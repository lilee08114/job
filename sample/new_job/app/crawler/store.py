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

#####################################
#this module provide some custom celery base task
# and the crawler initaitor, and celery tasks
#####################################

class whenFinishCrawlDetail(Task):

	def links_filter(self, identifier):
		'''get the job sites whose 'have_detail' is False, then filter it base on the given identifier

		identifier: string, must be one of ['qc', 'lp', 'lg'] 
		return: list, contains tuples, each tuple contains the job's db row id and job's url
		'''
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
		'''this method override the original on_seccess
		this method will start the crawler for job's detail. when the celery task succeed
		
		args: list, 1st element is the Crawler class instance
					2nd element is the flag to mark is this a schedule task
					3rd element is the identifier to filter the job url, url will be sent
					 	to different crawler base the identifier
		'''
		ins = args[0]  
		is_subscribe = args[1]
		identifier = args[2]
		links = self.links_filter(identifier)
		logging.info('identifier: {}, links:{}, ins:{}, is_subscribe:{}'.\
			format(identifier, links, ins, is_subscribe))
		for link in links:
			if identifier == 'qc':
				Crawler.qc_detail.apply_async((ins, link[0], link[1], is_subscribe))
			elif identifier == 'lp':
				Crawler.lp_detail.apply_async((ins, link[0], link[1], is_subscribe))
			elif identifier == 'lg':
				Crawler.lg_detail.apply_async((ins, link[0], link[1], is_subscribe))
		
class whenFinishUpdateStatus(Task):

	def on_success(self, retval, task_id, args, kwargs):
		'''this method override the original on_seccess, mark whether a job url has been crawled,
		if this celery task is a schedule task, this method will update the 'Subscribe' status
		
		args: list, 1st element is the Crawler class instance
					2nd element is job's db row id
		'''
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
		'''crawler initiator, this class is used to start the crawler'''
		self.key_word = key_word
		#get 30 proxy ips
		self.proxy = ProxyPool.get_30_proxies('qc')
		#base on the keyword, generate the job_list url
		link = Links(key_word)
		self.qc = Crawler_for_51job(link.qianCheng(), self.proxy, key_word)
		self.lp = Crawler_for_Liepin(link.liePin(), self.proxy, key_word)
		self.lg = Crawler_for_Lagou(link.laGou(), self.proxy, key_word)


	def subsequent_tasks(self, days, interval):
		'''generate the schedule tasks.  rather than a real schedule tasks, this is implemented by
		generating many tasks base one the days and interval, and each task will be assaigned 
		a proper 'coundown' argument value, so this task will be ran in particular moment
		during a period

		days: positive integer, how many days the schedule tasks keep running
		interval: positive integer, interval between tasks
		return: tuple, contains 3 list, each list contains the subsequent tasks 
		'''
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
		'''the crawler is started here

		subscribe: if True, means that this is a subscribed task, there will be 
					subsequent tasks added to the task's 'link' argument
		days: positive integer, how many days the schedule tasks keep running
		interval: positive integer, interval between tasks
		'''
		#link决定是否有后续的任务
		#如果有subscribe，则有link任务，link任务中带有countdown参数
		#z这里的subscribe主要是决定在详情抓取任务完成后是否更新subscirbe数据库信息
		subseq_qc = subseq_lp = subseq_lg = None
		if subscribe:
			subseq_qc, subseq_lp, subseq_lg = self.subsequent_tasks(days, interval)

		Crawler.qc_list.apply_async((self, subscribe, 'qc'), link=subseq_qc)
		Crawler.lp_list.apply_async((self, subscribe, 'lp'), link=subseq_lp)
		Crawler.lg_list.apply_async((self, subscribe, 'lg'), link=subseq_lg)

	@ce.task(base=whenFinishCrawlDetail)
	def qc_list(self, subscribe, identifier='qc'):
		'''start the 51job_list crawler, when finishing, the crawler for job's detail will be started

		subscribe: boolean, decide whether start the subsequent task when this task finish
		'''
		self.qc.job_list()

	@ce.task(base=whenFinishCrawlDetail)
	def lp_list(self, subscribe, identifier='lp'):
		'''start the liepin_list crawler, when finishing, the crawler for job's detail will be started

		subscribe: boolean, decide whether start the subsequent task when this task finish
		'''
		self.lp.job_list()

	@ce.task(base=whenFinishCrawlDetail)
	def lg_list(self, subscribe, identifier='lg'):
		'''start the lagou_list crawler, when finishing, the crawler for job's detail will be started

		subscribe: boolean, decide whether start the subsequent task when this task finish
		'''
		self.lg.job_list()

	@ce.task(base=whenFinishUpdateStatus)
	def qc_detail(self, job_id, job_link, subscribe):
		'''start the 51job_detail crawler

		job_id: integer, the job's db row id
		job_link: string, the job's url
		subscribe: boolean, decide whether update the Subscribe table when this task finish
		'''
		self.qc.job_detail(job_id, job_link)

	@ce.task(base=whenFinishUpdateStatus)
	def lp_detail(self, job_id, job_link, subscribe):
		'''start the liepin_detail crawler

		job_id: integer, the job's db row id
		job_link: string, the job's url
		subscribe: boolean, decide whether update the Subscribe table when this task finish
		'''
		self.lp.job_detail(job_id, job_link)

	@ce.task(base=whenFinishUpdateStatus)
	def lg_detail(self, job_id, job_link, subscribe):
		'''start the lagou_detail crawler

		job_id: integer, the job's db row id
		job_link: string, the job's url
		subscribe: boolean, decide whether update the Subscribe table when this task finish
		'''
		self.lg.job_detail(job_id, job_link)



