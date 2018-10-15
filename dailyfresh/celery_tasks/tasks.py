from celery import Celery
from django.core.mail import send_mail


app = Celery('celery_tasks.tasks', broker='redis://192.168.12.209:6379/3')

#给celery可以使用django的导入模块
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")#在项目的wsgi.py文件中
django.setup()#可以使用django模块

# celery -A celery_tasks.tasks worker -l info
# celery -A celery_tasks.tasks worker --loglevel=info


@app.task
def task_send_email(subject, message, sender, receive, html_message):
    print("发送邮件开始，。。。。")
    send_mail(subject, message, sender, receive, html_message=html_message)
    print("发送邮件结束，。。。。")
