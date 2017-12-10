import re
from datetime import datetime, timedelta

from sqlalchemy import text
from sqlalchemy.sql import and_
import jieba.analyse
from app.model import User, Jobbrief, Jobdetail, Company, Jobsite, Subscribe

class Format():
	#公共类，负责将直接从网页上抓取的内容进行格式化并存储！
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
		'''is the job new to us?
		'''
		stmt = text("SELECT * " 
					"FROM brief LEFT OUTER JOIN company "
						"ON company.id = brief.company_id "
					"WHERE brief.job_name = :j_name " 
					"AND brief.job_salary_low = :salary_l "
					"AND brief.job_salary_high = :salary_h "
					"AND company.company_name = :comp_name ")
		check = Jobbrief.query.from_statement(stmt).params(
			j_name=j_name, salary_l=salary[0], salary_h=salary[1], comp_name=comp_name
													).first()
		if check is None:
			return 'new_job'
		else:
			return 'end'

		'''
		check = Jobbrief.query.filter_by(job_name=j_name, 
					job_salary_low=salary[0], job_salary_high=salary[1]
					).join(Company).filter_by(company_name=comp_name)

		if check.first() is None:
			return 'new_job'
			
		elif Jobbrief.query.filter_by(job_name=j_name, job_time=job_time,
					job_salary_low=salary[0], job_salary_high=salary[1]
					).join(Company).filter_by(
					company_name=comp_name).first():
			return 'end'
		
		#else:						
		#	return 'repeated job'
		'''

	def save_company(self, jobinfo):
		'''if the company is new to us,save it
		'''
		comp = Company(company_name=jobinfo['company_name'],
						company_site=jobinfo['company_site'])
		return comp._save()

	def save_site(self, jid, link):
		job_site = Jobsite(site=link, brief_id=jid)
		job_site._save()	


	def save_job(self, comp_id, jobinfo):
		new_job = Jobbrief(key_word=self.keyword, 
						job_name=jobinfo['job_name'],
						job_location=jobinfo.get('job_location'), 
						job_salary_low=jobinfo['salary'][0],
						job_salary_high=jobinfo['salary'][1],
						job_edu=jobinfo.get('edu'),
						job_quantity=jobinfo.get('quantity'),
						job_time=jobinfo['pub_time'],
						job_other_require=jobinfo.get('other_requirement'),
						job_labels=',\n'.join(jobinfo.get('job_labels')) if \
										jobinfo.get('job_labels') is not None else None,
						company_id=comp_id,
						job_exp = self.exp_format(jobinfo.get('exp'))
						)
		return new_job._save()	#return brief_id or false


	def save_raw_info(self, jobinfo):
		'''just write the raw information about the job into database
		param:
			job_infos: a dict represents a job
		return a list containing many dicts, each dict represents a
			job's information including 'id','exp','job_site'
		'''
		jobinfo['salary'] = self.salary_format(jobinfo['salary'])
		jobinfo['pub_time'] = self.pub_time_format(jobinfo['pub_time'])

		check = self.info_check(jobinfo['salary'], jobinfo['company_name'],
						jobinfo['job_name'], jobinfo['pub_time'])	
		if check == 'end':
			#no more new job, stop searching
			return True
		elif check == 'repeated job':
			#this is a repeated job, so just save the website
			#without foreignkey, is still work?
			job_id = Jobbrief.query.filter_by(job_name=jobinfo['job_name'], 
				job_salary_low=jobinfo['salary'][0], job_salary_high=jobinfo['salary'][1]).\
				join(Jobbrief.company).filter_by(company_name=jobinfo['company_name']).\
				first().id
			site = Jobsite(brief_id=int(job_id), site=jobinfo['link'])
			site._save()
			return False
		elif check == 'new_job':
			#new job, save it!
			#job_dict = {}
			comp_id = self.save_company(jobinfo)
			job_id = self.save_job(comp_id, jobinfo)
			if job_id:
				self.save_site(job_id, jobinfo['link'])
			return False

	def save_detail_info(self, job_id, job_detail):
		new_detail =  Jobdetail(requirement=job_detail, brief_id=job_id)
		new_detail._save()
		#could update have_derail status in jobsite table!
		

	def extract_labels(self, sentence):
		sentence = sentence.encode()
		labels = jieba.analyse.extract_tags(sentence, topK=8)
		return labels

