
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


	def _save(self):
		#if success return True, otherwise False
		db.session.add(self)
		try:
			db.session.commit()
			print ('save {} successfully!'.format(self))
			print ('--------LOOK THE TABLE ID----------')
			print (self.id)
			print ('--------LOOK THE TABLE ID  END----------')
			return self.id
		except:
			db.session.rollback()
			print ('save {} failed!'.format(self))
			return False


	def delete(cls, pk):
		table = cls.query.filter_by(criteria).first()

	def _update(self, **kwargs):

		for k, v in  kwargs.items():
			setattr(self, k, v)
		return self._save()


	def get():
		pass