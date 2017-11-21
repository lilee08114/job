import re
import json
import logging
from datetime import datetime, timedelta
from flask import current_app, Flask
from celery import Task, group, chain
import jieba.analyse
from .crawlerHandler import CrawlerHandler
from ..model import db, User, Jobbrief, Jobdetail, Company, Jobsite, Subscribe
from app.celery import ce


#这个module相互引用太严重，是很脆弱的，最好能切分开
class MyQCTask(Task):

	def on_success(self, retval, task_id, args, kwargs):
		'''rewrite the method, When a task finish, it will call another series tasks to implement periodic task.
		'''
		period_time = kwargs.get('period_time')
		ins = args[0]		
		if period_time is not None  and  len(period_time) != 0:
			logging.warning('QC Subscribe: key: %s countdown for %sth time'\
				%(ins.keyword,len(period_time)))
			tm = period_time.pop(0)
			
			chain(fetch_Store.Start_qc_raw.s(ins, period_time=period_time), 
				fetch_Store.qc_dmap.s(fetch_Store.Start_qc_detail.s(), ins)).apply_async(countdown=tm)

		#当全部任务结束时，这里需要存储相关subscribe结束时间信息
			if len(period_time)==0:
				keyword = ins.keyword
				sub_obj = Subscribe.query.filter_by(sub_key=keyword).\
					order_by(Subscribe.sub_start.desc()).first()
				sub_obj.sub_end = datetime.utcnow() + timedelta(hours=8)
				logging.warning('Subscribe Task: key: %s end!'%ins.keyword)
				db.session.add(sub_obj)
				try:
					db.session.commit()
				except:
					db.session.rollback()
					raise


class MyLPTask(Task):

	def on_success(self, retval, task_id, args, kwargs):
		period_time = kwargs.get('period_time')
		ins = args[0]		
		if period_time is not None  and  len(period_time) != 0:
			logging.warning('LP Subscribe: key: %s countdown for %sth time'\
				%(ins.keyword,len(period_time)))
			tm = period_time.pop(0)
			
			chain(fetch_Store.Start_lp_raw.s(ins, period_time=period_time), 
			fetch_Store.lp_dmap.s(fetch_Store.Start_lp_detail.s(), ins)).apply_async(countdown=tm)
			
		#当全部任务结束时，这里需要存储相关subscribe结束时间信息
			if len(period_time)==0:
				keyword = ins.keyword
				sub_obj = Subscribe.query.filter_by(sub_key=keyword).\
					order_by(Subscribe.sub_start.desc()).first()
				sub_obj.sub_end = datetime.utcnow() + timedelta(hours=8)
				logging.warning('Subscribe Task: key: %s end!'%ins.keyword)
				db.session.add(sub_obj)
				try:
					db.session.commit()
				except:
					db.session.rollback()
					raise

class MyLGTask(Task):

	def on_success(self, retval, task_id, args, kwargs):
		period_time = kwargs.get('period_time')
		ins = args[0]		
		if period_time is not None  and  len(period_time) != 0:
			logging.warning('LG Subscribe: key: %s countdown for %sth time'\
				%(ins.keyword,len(period_time)))
			tm = period_time.pop(0)

			chain(fetch_Store.Start_lg_raw.s(ins, period_time=period_time), 
				fetch_Store.lg_dmap.s(fetch_Store.Start_lg_detail.s(), ins)).apply_async(countdown=tm)

		#当全部任务结束时，这里需要存储相关subscribe结束时间信息
			if len(period_time)==0:
				keyword = ins.keyword
				sub_obj = Subscribe.query.filter_by(sub_key=keyword).\
					order_by(Subscribe.sub_start.desc()).first()
				sub_obj.sub_end = datetime.utcnow() + timedelta(hours=8)
				logging.warning('Subscribe Task: key: %s end!'%ins.keyword)
				db.session.add(sub_obj)
				try:
					db.session.commit()
				except:
					db.session.rollback()
					raise

class fetch_Store():
	''' 1,in celery, worker needs context such as db connection
	to do jobs, so a new Flask instance is initiated here and  
	bind a new db connection onto that instance
		2, why not initiated the Flask instance in the constructor 
	method? cause for fetch_store instances ,i just need only one 
	Flask instance in addition 
		3, call class.method(instance, args) in the celery, instead of 
	instnce.method(args), cause instance cannot be pickled..only can be 
	transported as args
	'''
	ce.conf.update(
				CELERY_TASK_SERIALIZER='pickle',
				CELERY_DEFAULT_EXCHANGE='default',
				CELERY_DEFAULT_EXCHANGE_TYPE='direct',
				CELERY_DEFAULT_ROUTING_KEY='default',				
				)
	ce.conf.CELERY_TIMEZONE='Asia/Shanghai'
	new_app = Flask(__name__)
	new_app.config['SQLALCHEMY_DATABASE_URI'] = \
		'mysql+mysqlconnector://root:a123@localhost:3306/lilee'
	db.init_app(new_app)
	db.app = new_app
	#同上面一样，重新初始化logger
	log_format = '%(levelname)s:%(asctime)s:%(message)s'
	datefmt = '%Y/%m/%d %I:%M:%S'
	logging.basicConfig(filename='crawler.log', format=log_format,
		datefmt=datefmt, level=logging.INFO)


	def __init__(self, keyword, exp=None, edu=None, city='成都', 
					salary=None, pub_time=None, page=1 ):

		self.keyword = keyword
		initiator = CrawlerHandler(keyword, exp=exp, edu=edu, page=page,
				city=city, salary=salary, pub_time=pub_time)
		self.qcCrawlerInstance = initiator.QianChengLinkGenerator()
		self.lagouCrawlerInstance = initiator.lagouLinkGenerator()
		self.liepinCrawlerInstance = initiator.liepinLinkGenerator()		

	def pub_time_format(self, pub_time):
		'''transfer the time informations which in different type into a 
			common format to store, 5 kinds of time format are acceptable:
			['08-05发布','2017-08-04 22:15:00','15小时前','昨天',8-5，
			'前天','2017-07-30']
		'''
		if '发布' in pub_time:
			str_date = re.search('\d*-\d*',pub_time).group(0)
			return datetime.strptime(str_date, '%m-%d').replace(datetime.now().year)
		elif bool(re.match('\d*-\d*$', pub_time)):
			return datetime.strptime(pub_time, '%m-%d').replace(datetime.now().year)
		elif bool(re.search('前', pub_time)):
			if bool(re.match('^\d{1,2}小时', pub_time)):
				hours = int(re.search('^\d{1,2}', pub_time).group(0))
				return datetime.now()-timedelta(hours=hours)
			elif bool(re.match('^\d{1,2}天', pub_time)):
				days = int(re.search('^\d', pub_time).group(0))
				return datetime.now()-timedelta(days=days)
		elif '刚' in pub_time:
			return datetime.now()
		elif pub_time == '昨天':
			return datetime.now()-timedelta(days=1)
		elif pub_time == '前天':
			return datetime.now()-timedelta(days=2)
		else:
			try:
				return datetime.strptime(pub_time, '%Y-%m-%d')
			except ValueError:
				return datetime.strptime(pub_time, '%Y-%m-%d %H:%M:%S')

	def salary_format(self, salary):
		'''formate the salary information , accepted:
			['0.4-1万/月', '0.4-1千/月', '10K-15K','13-23万''面议']
		'''
		print ('-------%s-----'%salary)
		if not bool(re.search('\d', salary)):
			return 	[0,0]
		elif '万' in salary:
			salary_floor = salary.split('万')[0].split('-')[0]
			salary_ceil = salary.split('万')[0].split('-')[1]
			return [float(salary_floor)*10000, float(salary_ceil)*10000]
		elif '千' in salary:
			salary_floor = salary.split('千')[0].split('-')[0]
			salary_ceil = salary.split('千')[0].split('-')[1]
			return [float(salary_floor)*1000, float(salary_ceil)*1000]
		elif 'K' in salary:
			salary_floor = salary.split('-')[0].split('K')[0]
			salary_ceil = salary.split('-')[1].split('K')[0]
			return [float(salary_floor)*1000, float(salary_ceil)*1000]
		elif 'k' in salary:
			salary_floor = salary.split('-')[0].split('k')[0]
			salary_ceil = salary.split('-')[1].split('k')[0]
			return [float(salary_floor)*1000, float(salary_ceil)*1000]
		else:
			return [0,0]

	def exp_format(self, exp):
		'''fetch the lowest work experience requirement of the job,
			in database there should be two exp column, one store the
			origin requirement, another store the lowest requirment in
			int format so we can sort it conveniently
		'''
		if exp is None:
			return 0
		elif bool(re.search('\d', exp)) is False:
			return 0
		return int(re.search('\d{1,2}',exp).group(0))

	def info_check(self, salary, comp_name, j_name, job_time):
		'''check whether the job has alrady been stored, if yes then break
		and stop the crawler cause that means we have fetch all the newly
		posted job. 
		but jobs that have the sanme name, same company name, 
		and same salary but different pub time with someone which already 
		exists in the database will only add its link into Jobsite table
		cause it's a repeated job.
		others will be normally stored
		'''
		
		check = Jobbrief.query.filter_by(job_name=j_name, 
					job_salary_low=salary[0], job_salary_high=salary[1]
					).join(Jobbrief.company).filter_by(
					company_name=comp_name)
		if check.first() is None:
			return 'new_job'
			
		elif Jobbrief.query.filter_by(job_name=j_name, job_time=job_time,
					job_salary_low=salary[0], job_salary_high=salary[1]
					).join(Jobbrief.company).filter_by(
					company_name=comp_name).first():
			return 'end'
		
		else:
			return 'repeated job'
		

	def save(self, table):
		db.session.add(table)
		try:
			db.session.commit()
			logging.info('write db info %(table)s successfully')
		except:
			db.session.rollback()
			logging.warning('write db info %(table)s fail')
			raise
	
	
	#-------------------MyQCTask
	@ce.task(name='fetch_Store.Start_qc_raw', base=MyQCTask)
	def Start_qc_raw(self, period_time=None):	
		raw_qc_infos = self.qcCrawlerInstance.fetchJobLink()
		return self.save_raw_info(raw_qc_infos)

	@ce.task(name='fetch_Store.Start_lp_raw', base=MyLPTask)
	def Start_lp_raw(self, period_time=None):
		raw_lp_infos = self.liepinCrawlerInstance.fetchJobLink()
		return self.save_raw_info(raw_lp_infos)
		
	@ce.task(name='fetch_Store.Start_lg_raw', base=MyLGTask)
	def Start_lg_raw(self, period_time=None):
		raw_lg_infos = self.lagouCrawlerInstance.fetchJobLink()
		return self.save_raw_info(raw_lg_infos)
	#above three functions will return a list containing many dicts
	#-----------------------------------------
	@ce.task(name='fetch_Store.qc_dmap', queue='qc')
	def qc_dmap(pre_result, callback, ins):
		'''parameters:
		pre_result: list, return by method 'Start_qc_raw'
		callback: signature, signature of celery task Start_qc_detail 
		ins: instance of the fetch_Store class

		return: None, every element in the pre_result will be passed to callback task to
				generates many parallel tasks.
		'''
		return group(callback(ins, i, ) for i in pre_result)

	@ce.task(name='fetch_Store.lp_dmap', queue='lp')
	def lp_dmap(pre_result, callback, ins):	
		#same as qc_map, but pre_result from Start_lp_raw, and generate Start_lp_detail
		
		return group(callback(ins, i, ) for i in pre_result)

	@ce.task(name='fetch_Store.lg_dmap', queue='lg')
	def lg_dmap(pre_result, callback, ins):	
		#same as qc_map, but pre_result from Start_lg_raw, and generate Start_lg_detail
		return group(callback(ins, i, ) for i in pre_result)

	@ce.task(name='fetch_Store.Start_qc_detail')
	def Start_qc_detail(self, link):
		id = link['id']
		jobinfo = self.qcCrawlerInstance.jobDetail(link)  #return a dict
		job_detail = Jobdetail(requirement=',\n'.join(jobinfo.get('job_requirement')),
								brief_id=id)
		self.save(job_detail)
		#extract labels of the requirement, it may quiet waste time.
		sentence = ' '.join(jobinfo.get('job_requirement')).encode()
		label = jieba.analyse.extract_tags(sentence, topK=8)
	
		job = Jobbrief.query.filter_by(id=id).first_or_404()		
		job.job_exp = self.exp_format(jobinfo['exp'])
		job.job_edu = jobinfo.get('edu')
		job.job_quantity = jobinfo.get('quantity')
		job.job_other_require = jobinfo.get('other_requirement')
		job.job_labels = ', '.join(label)
		self.save(job)

		

	@ce.task(name='fetch_Store.Start_lp_detail')
	def Start_lp_detail(self, link):
		id = link['id']
		jobinfo = self.liepinCrawlerInstance.jobDetail(link)
		job_detail = Jobdetail(requirement=',\n'.join(jobinfo.get('job_requirement')),
										brief_id=id)
		self.save(job_detail)
		#extract labels of requiremrnt
		sentence = ' '.join(jobinfo.get('job_requirement')).encode()
		label = jieba.analyse.extract_tags(sentence, topK=8)
		
		#formatted_exp = self.exp_format(jobinfo['exp'])
		job = Jobbrief.query.filter_by(id=id).first_or_404()
		job.job_exp = self.exp_format(jobinfo['exp'])
		job.job_labels = ', '.join(label)
		self.save(job)	
		
	@ce.task(name='fetch_Store.Start_lg_detail')	
	def Start_lg_detail(self, link):
		jobinfo = self.lagouCrawlerInstance.jobDetail(link)  #return a dict
		id = link['id']
		job = Jobbrief.query.filter_by(id=id).first_or_404()
		job.job_exp = self.exp_format(jobinfo['exp'])
		job.job_labels=', '.join(jobinfo.get('job_labels'))
		self.save(job)

		job_detail = Jobdetail(requirement=',\n'.join(jobinfo.get('job_requirement')),
										brief_id=id)
		self.save(job_detail)
	'''
	@ce.task(name='store.Start_lp')
	def Start_lp(self):
		logging.info('[LieP] starting LP...')
		lp = self.liepinCrawlerInstance.jobDetail()
		self.qcHandler(lp)
		logging.info('[LieP] finish LP...')
		

	@ce.task(name='store.Start_lg')
	def Start_lg(self):
		logging.info('[LG] starting LG...')
		lg = self.lagouCrawlerInstance.jobDetail()
		self.qcHandler(lg)
		logging.info('[LG] finish LG...')
	

	def workStart(self):
		#it's obviously better to search and save each
		#site one by one, so that even something wrong 
		#happens we won't lost all previous effort
		
		print ('Now lets search works from 51job.com ')
		qc = self.qcCrawlerInstance.jobDetail()
		print ('Fetch info from 51 succedd!')
		self.qcHandler(qc)
		print ('Save info succedd!')
		print ('Now lets search works from liepin.com ')
		lp = self.liepinCrawlerInstance.jobDetail()
		print ('Fetch info from liepin succedd!')	
		self.qcHandler(lp)
		print ('Save info succedd!')
		print ('Now lets search works from liepin.com ')	
		lg = self.lagouCrawlerInstance.jobDetail()
		print ('Fetch info from lagou succedd!')
		self.qcHandler(lg)
		print ('Save info succedd!')
	'''

	def save_raw_info(self, job_infos):
		'''just write the raw information about the job into database
		param:
			job_infos: a list containing many dicts, each dict 
				represents a job
		return a list containing many dicts, each dict represents a
			job's information including 'id','exp','job_site'
		'''
		link_list = []
		for jobinfo in job_infos:
			formatted_salary = self.salary_format(jobinfo['salary'])
			formatted_pub_time = self.pub_time_format(jobinfo['pub_time'])
			check = self.info_check(formatted_salary, jobinfo['company_name'],
									jobinfo['job_name'], formatted_pub_time)
			if check == 'end':
				print ('this job is already exist, save process end')
				break
			elif check == 'repeated job':
				print ('this job is repeated, save process end')
				job_id = Jobbrief.query.filter_by(job_name=jobinfo['job_name'], 
					job_salary_low=formatted_salary[0], job_salary_high=formatted_salary[1]).\
					join(Jobbrief.company).filter_by(company_name=jobinfo['company_name']).\
					first().id
				site = Jobsite(brief_id=int(job_id), site=jobinfo['link'])
				self.save(site)
			elif check == 'new_job':
				print ('this job is a new job')
				job_dict = {}
				company = Company.query.filter_by(
									company_name=jobinfo['company_name']).first()
				if company is None:
					comp = Company(company_name=jobinfo['company_name'],
									company_site=jobinfo['company_site'])
					self.save(comp)
					print ('new company relative information has been saved!')
				job = Jobbrief(key_word=self.keyword, job_name=jobinfo['job_name'],
								job_location=jobinfo.get('job_location'), 
								job_salary_low=formatted_salary[0],
								job_salary_high=formatted_salary[1],
								#job_exp=self.exp_format(jobinfo['exp']),
								job_edu=jobinfo.get('edu'),
								job_quantity=jobinfo.get('quantity'),
								job_time=self.pub_time_format(jobinfo['pub_time']),
								job_other_require=jobinfo.get('other_requirement'),
								job_labels=',\n'.join(jobinfo.get('job_labels')) if \
										jobinfo.get('job_labels') is not None else None,
								company_id=int(Company.query.filter_by(
									company_name=jobinfo['company_name']).first().id)
								)
					
				db.session.add(job)
				job_id = job.id
				db.session.commit()				
				job_site = Jobsite(site=jobinfo['link'], brief_id=job.id)
				self.save(job_site)	
				job_dict['id'] = job.id
				job_dict['key'] = self.keyword
				job_dict['link'] = jobinfo['link']				
				job_dict['exp'] = jobinfo.get('exp')
				link_list.append(job_dict)
				#link_list.append(dict([('id',job_id),('link',job_site),('exp',jobinfo.get('exp'))]))
		
		return link_list


	'''
	def qcHandler(self, job_collection):
		#if the job new?
		#NO, stop immediately
		#Repeated job, only write its link into Jobsite table
		#YES, write the company link ——> write the job brief
		#	——>write the requirement ——> write the job link
			

		for jobinfo in job_collection:
			formatted_salary = self.salary_format(jobinfo['salary'])
			formatted_exp = self.exp_format(jobinfo['exp'])
			formatted_pub_time = self.pub_time_format(jobinfo['pub_time'])
			check = self.info_check(formatted_salary, jobinfo['company_name'],
									jobinfo['job_name'], formatted_pub_time)
			if check == 'end':
				print ('this job is already exist, save process end')
				break
			elif check == 'repeated job':
				job_id = Jobbrief.query.filter_by(job_name=jobinfo['job_name'], 
					job_salary_low=formatted_salary[0], job_salary_high=formatted_salary[1]).\
					join(Jobbrief.company).filter_by(company_name=jobinfo['company_name']).\
					first().id
				site = Jobsite(brief_id=int(job_id), site=jobinfo['link'])
				self.save(site)
				print ('a repeated job site has been saved!')
			elif check == 'new_job':
				company = Company.query.filter_by(
									company_name=jobinfo['company_name']).first()
				if company is None:
					comp = Company(company_name=jobinfo['company_name'],
									company_site=jobinfo['company_site'])
					self.save(comp)
					print ('new company relative information has been saved!')
				job = Jobbrief(key_word=self.keyword, job_name=jobinfo['job_name'],
								job_location=jobinfo.get('job_location'), 
								job_salary_low=formatted_salary[0],
								job_salary_high=formatted_salary[1],
								job_exp=self.exp_format(jobinfo['exp']),
								job_edu=jobinfo['edu'],
								job_quantity=jobinfo.get('quantity'),
								job_time=self.pub_time_format(jobinfo['pub_time']),
								job_other_require=jobinfo.get('other_requirement'),
								job_labels=json.dumps(jobinfo.get('job_labels')),
								company_id=int(Company.query.filter_by(
									company_name=jobinfo['company_name']).first().id))
				self.save(job)
				print ('job relative information has been saved!')
				job_detail = Jobdetail(requirement=json.dumps(jobinfo['job_requirement']),
										brief_id=job.id)
				self.save(job_detail)
				print ('job-requirement has been saved!')
				job_site = Jobsite(site=jobinfo['link'], brief_id=job.id)
				self.save(job_site)
				print ('new job site has been saved!')
	'''

