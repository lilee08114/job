
from celery import Task

class MyBase(Task):
	def on_success(self, retval, task_id, args, kwargs):
		#在任务结束时更改时间