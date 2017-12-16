from .suite import BaseSuite
import unittest
from app.crawler.lagou import Crawler_for_Lagou
import gzip
from io import BytesIO



class TestA(BaseSuite):
	'''
	def test_open(self):

		url = 'https://www.lagou.com/jobs/1548255.html'
		proxy =[('Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
			{'https':'http://119.23.141.97:9000'})]
		keyword = 'python'
		ins = Crawler_for_Lagou(url, proxy, keyword)
		x = ins.open_url('https://www.lagou.com/jobs/1548255.html')
		y = gzip.GzipFile(fileobj=BytesIO(x))
		html = y.read().decode()
		print (html)
		{'https':'120.40.38.25:808'}
	'''

	def test_open_1(self):
		url = 'https://www.lagou.com/jobs/positionAjax.json?px=default&city=%E6%88%90%E9%83%BD&needAddtionalResult=false&isSchoolJob=0'
		#url = 'http://httpbin.org/post'
		proxy =[('Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
			{'https':'123.152.77.89:8118'})]
		keyword = 'python'
		ins = Crawler_for_Lagou(url, proxy, keyword)
		ins.job_list()

