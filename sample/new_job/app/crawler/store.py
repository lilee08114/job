import re
import json
import logging
from datetime import datetime, timedelta
from flask import current_app, Flask
from celery import Task, group, chain
import jieba.analyse
from .crawlerHandler import Links
from ..model import db, User, Jobbrief, Jobdetail, Company, Jobsite, Subscribe
from app.celery import ce
from . import Format ,whenFinishCrawlDetail, whenFinishUpdateDetail
from lagou import Crawler_for_Lagou
from liepin import Crawler_for_Liepin
from qiancheng import Crawler_for_51job
from proxy_pool import ProxyPool

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

	def subsequent_tasks(self, days, interval):
		#根据间隔的天数获取任务的countdown数列，据此生成后续的所有任务对象
		#以list形式返回
		ct = []
		ct_time = interval
		while ct_time < days*24*60*60:
			ct.append(ct_time)
			ct_time += interval
			

		subsequent_qc = [self.qc_list.apply_async((True,), countdown=i) for i in ct]
		subsequent_lp = [self.lp_list.apply_async((True,), countdown=i) for i in ct]
		subsequent_lg = [self.lg_list.apply_async((True,), countdown=i) for i in ct]
		return (subsequent_qc, subsequent_lp, subsequent_lg)

	def Start(self, subscribe=False, days=3, interval=5*60*60):
		#link决定是否有后续的任务
		#如果有subscribe，则有link任务，link任务中带有countdown参数
		#z这里的subscribe主要是决定在详情抓取任务完成后是否更新subscirbe数据库信息
		subseq_qc, subseq_lp, subseq_lg = None
		if subscribe:
			subseq_qc, subseq_lp, subseq_lg = self.subsequent_tasks(days, interval)

		self.qc_list.aplly_async((subscribe), link=subseq_qc)
		self.lp_list.apply_async((subscribe), link=subseq_lp)
		self.lg_list.apply_async((subscribe), link=subseq_lg)


	@ce.task(base=whenFinishCrawlDetail)
	def qc_list(self, subscribe, identifier='qc'):
		#identifier 主要是决定在on_success回调函数中，调用哪一个网站的抓取程序
		#当QC完成，应当更具identifier来调用QC的详情抓取
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

	@ce.task(base=whenFinishUpdateDetail)
	def qc_detail(self, job_id, job_link, subscribe):
		#subscribe决定是否在on_success回调中更新subscribe信息
		#job_id在保存时需要
		self.qc.job_detail(job_id, job_link)

	@ce.task(base=whenFinishUpdateDetail)
	def lp_detail(self, job_id, job_link, subscribe):
		self.lp.job_detail(job_id, job_link)

	@ce.task(base=whenFinishUpdateDetail)
	def lg_detail(self, job_id, job_link, subscribe):
		self.lg.job_detail(job_id, job_link)




