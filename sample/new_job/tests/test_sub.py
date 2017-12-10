#如何测试？
#是测试每个func， 还是直接测试整个功能？
import re
from .suite import BaseSuite
from app.proxy import GetIps
from app.model import Ip_pool, Jobbrief, Company, Jobsite, Jobdetail
from app.crawler import Format
from app.crawler.crawlerHandler import Links
from app.crawler.proxy_pool import ProxyPool
from app.crawler.qiancheng import Crawler_for_51job
from app.crawler.liepin import Crawler_for_Liepin
from app.crawler.lagou import Crawler_for_Lagou


class TestProxy(BaseSuite):

	def test_proxy(self):
		#should fetch at least 30 proxies!
		gp = GetIps()
		gp.fresh_ip(check=False)
		with self.app.app_context():
			proxy = Ip_pool.query.all()
		self.assertLessEqual(30, len(proxy))

class TestFormat(BaseSuite):

	def test_time_format(self):
		valid_test_time = ['08-05发布','2017-08-04 22:15:00','15小时前','昨天','8-5',
					'前天','2017-07-30']
		for time in valid_test_time:
			formatted_time = Format().pub_time_format(time)
			self.assertRegex(formatted_time, '^(\d{4})-(0\d{1}|1[0-2])-(0\d{1}|[12]\d{1}|3[01])')

		invalid_test_time = ['aa', '111', 111, ' ', '8-4', '前']
		for time in invalid_test_time:
			formatted_time = Format().pub_time_format(time)
			self.assertIsNone(formatted_time)

	def test_salary_format(self):
		valid_test_salary = ['0.4-1万/月', '0.4-1千/月', '10K-15K','13-23万','面议']
		for salary in valid_test_salary:
			formatted_salary = Format().salary_format(salary)
			is_int = [isinstance(i, int) for i in formatted_salary]
			self.assertTrue(all(is_int))
			self.assertLessEqual(formatted_salary[0], formatted_salary[1])

		invalid_test_salary = ['112-1212', '12343', 'sadas', '-111-112', '测试']
		for salary in valid_test_salary:
			formatted_salary = Format().salary_format(salary)
			self.assertEqual([0, 0], formatted_salary)

	def test_info_check(self):
		#需要事先插入一些数据
		with self.app.app_context():
			#new job
			is_new_job = Format().info_check(salary, comp_name, j_name, j_time)
			self.assertEqual(is_new_job, 'new_job')
			#not new job
			is_new_job = Format().info_check(salary, comp_name, j_name, j_time)
			self.assertEqual(is_new_job, 'end')

	def test_job_crawler(self):
		#首先测试工作列表抓取
		self.login()
		key_word =  'python'
		gp = GetIps()
		gp.fresh_ip(check=False)
		proxy = ProxyPool.get_30_proxies('qc')
		link = Links(key_word)
		qc = Crawler_for_51job(link.qianCheng(), proxy, key_word)
		lp = Crawler_for_Liepin(link.liePin(), proxy, key_word)
		lg = Crawler_for_Lagou(link.laGou(), proxy, key_word)
		qc.job_list()
		lp.job_list()
		lg.job_list()

		with self.app.app_context():
			result = Jobbrief.query
		#确认Jobbrief表插入成功
		self.assertLessEqual(1, len(result.all()))
		job = result.first()
		self.assertEqual(job.key_word, key_word)
		self.assertIsNotNone(job.job_name)
		self.assertIsNotNone(job.company_id)

		with self.app.app_context():
			#确认company表插入成功
			comp = Company.query.get(job.company_id)
			self.assertIsNotNone(comp)
			#确认jobsite表插入成功，且heve_detail为false	
			site = Jobsite.query.filter_by(brief_id=job.id).first()
			self.assertIsNotNone(site)
			self.assertFalse(site.have_detail)
			sites = Jobsite.query.filter_by(have_detail=False).all()
		#将对应网站导入到对应的爬虫
		qc_site = lp_site = lg_site = None
		for site_obj in sites:
			
			site = site_obj.site
			if 'liepin' in site:
				lp_site = site_obj
			if 'lagou' in site:
				lg_site = site_obj
			if '51job' in site:
				qc_site = site_obj
		if qc_site:
			brief_id = qc_site.brief_id
			#开始抓取详情
			qc.job_detail(brief_id, qc_site.site)
			#确认jobsite的have_detail已为True
			updated_site = Jobsite.query.filter_by(brief_id=brief_id).first()
			#因为have_detail在on_success中更新，所以测试中测不出
			#self.assertTrue(updated_site.have_detail)
			#确认jobbiref的job_labels已填充
			job_labels = Jobbrief.query.get(brief_id).job_labels
			self.assertIsNotNone(job_labels)
			#确认jobdetial表插入成功
			job_detail = Jobdetail.query.filter_by(brief_id=brief_id).first()
			self.assertIsNotNone(job_detail)

		if lp_site:
			brief_id = lp_site.brief_id
			lp.job_detail(brief_id, lp_site.site)
			updated_site = Jobsite.query.filter_by(brief_id=brief_id).first()
			#self.assertTrue(updated_site.have_detail)
			#确认jobbiref的job_labels已填充
			job_labels = Jobbrief.query.get(brief_id).job_labels
			self.assertIsNotNone(job_labels)
			#确认jobdetial表插入成功
			job_detail = Jobdetail.query.filter_by(brief_id=brief_id).first()
			self.assertIsNotNone(job_detail)

		if lg_site:
			brief_id = lg_site.brief_id
			lg.job_detail(brief_id, lg_site.site)
			updated_site = Jobsite.query.filter_by(brief_id=brief_id).first()
			#self.assertTrue(updated_site.have_detail)
			#确认jobbiref的job_labels已填充
			job_labels = Jobbrief.query.get(brief_id).job_labels
			self.assertIsNotNone(job_labels)
			#确认jobdetial表插入成功
			job_detail = Jobdetail.query.filter_by(brief_id=brief_id).first()
			self.assertIsNotNone(job_detail)




		
