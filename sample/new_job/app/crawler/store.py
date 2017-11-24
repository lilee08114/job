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
from . import Format 
from lagou import Crawler_for_Lagou
from liepin import Crawler_for_Liepin
from qiancheng import Crawler_for_51job

#这个module相互引用太严重，是很脆弱的，最好能切分开

#根据视图传来的URL和PROXY， 调用crawler的list，结束后从数据库搜寻site，进行详情抓取








