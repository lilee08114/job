
from flask_mail import Message
from flask import render_template, url_for
#define the assistant function here
from app.extensions import db, mail

def send_mail():
	msg = Message(subject='Please Confirm your Mail',
				recipients=[target_mail]
				)
	link = url_for('user.confirm_mail', token=token, _external=True)
	msg.html = render_template('send_mail.html', link=link, 
								user=name)
	mail.send(msg)

class Assessment():
	pass

class CRUD_Model(db.Model):
	#here we add the CRUD functions for database
	def save(self, table=None):
		#receive table obj and save it !what about the app_context?
		#in crawler need app_context
		if table is None:
			db.session.add(self)
		else:
			db.session.add(table)
		try:
			db.session.commit()
			print ('save one job successfully!')
		except:
			db.session.rollback()
			print ('save one failed!')

	@classmethod
	def add(cls, pk):
		#add additional info to particular data table
		if not isinstance(pk, int):
			try:
				pk = int(pk)
			except Exception, e:
				print ('pk shoud be a integer!')
				print (e)
				abort 404
		table = cls.query.get(pk)

	def delete(cls, pk):
		table = cls.query.filter_by(criteria).first()

	def update():
		pass

	def get():
		pass