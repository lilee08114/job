import re
from flask import Blueprint, render_template, request
from flask import redirect, url_for, flash
from flask_login import current_user
from app.model import Jobbrief, Jobdetail, Company
from app.model import Jobsite, User, Assessment, Profile



bp = Blueprint('front', __name__)

@bp.route('/')
def home():
    #form = SearchForm()
    key = request.args.get('key_word')
    page = int(request.args.get('page', 1))
    if key is not None:
        if key.strip() is '':
            flash('A key word is needed!')
            return render_template('home.html') 
        elif not bool(re.search('^[a-zA-Z\u4e00-\u9fa5]+$', key)):
            flash('must be Chinese or English letters only')
            return render_template('home.html')
        else:
            jobs = Jobbrief.query.filter_by(key_word=key)      
            if jobs.first() is None:
                flash('Sorry! This is a new word for us, please \
                    head to subscribe to start the crawling')
                return render_template('home.html')
            else:
                paginate = jobs.order_by(Jobbrief.job_time.desc()).paginate(page=page, per_page=10)
                #ave = Assessment.query.filter_by(key_word=key).first().average_salary
                return render_template('show_job.html', key=key, paginate=paginate)
                                #job=jobs.order_by(Jobbrief.job_time.desc()).limit(10).all())
    return render_template('home.html')

def satisfy(paginate, key):
    '''iterate the jobs in paginate object, compare it with current user's expectation to see
    whether a job satisfy the user's expectation
    paginate: Flask-Sqlalchemy.paginate object
    key: inquery key word
    '''
    score = []
    expect_obj = Profile.query.filter_by(user_id=current_user.id).first()
    if expect_obj is None:
        return []
    else:
        expect_salary = expect_obj.expect_salary  #1000
        expect_exp = expect_obj.exp               #3
        expect_edu = expect_obj.edu               #
        for item in paginate.items:
            pass


@bp.route('/detail/<int:job_id>/')
def detail(job_id):
    #需要改进！
    job_obj = Jobbrief.query.filter_by(id=job_id).first_or_404()
   
    job_detail = Jobdetail.query.filter_by(brief_id=job_id).first_or_404().requirement
   
    #job_detail = json.loads(job_detail)
    return render_template('jobs.html', job=job_obj, detail=job_detail)


@bp.route('/fresh/')
def fresh():
    from app.proxy.proxy_crawler import GetIps
    x = GetIps()
    x.fresh_ip()
    return render_template('home.html')
