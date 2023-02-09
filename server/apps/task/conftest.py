import os
import sys
import smtplib
from pathlib import Path
from email.mime.base import MIMEBase
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

from utils.constant import BUSINESS


def send_mail(task_status='SUCCESS'):
    me = BUSINESS.EMAIL_FROM
    my_password = BUSINESS.EMAIL_PASSWORD
    you = 'shuhaojie@unionstrongtech.com,songyouli@unionstrongtech.com'

    if task_status == 'SUCCESS':
        subject = 'CFD任务测试!!!'
        message = '附件为encas文件!!!'
    else:
        subject = 'CFD任务测试!!!'
        message = '附件为日志文件!!!'

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = ', '.join(you.split(','))
    msg.attach(MIMEText(message))

    file_path = '/workspaces/data/archive/20230208172439001/ensight_result.encas'
    part = MIMEBase('application', "octet-stream")
    with open(file_path, 'rb') as file:
        part.set_payload(file.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition',
                    'attachment; filename={}'.format(Path(file_path).name))
    msg.attach(part)

    s = smtplib.SMTP_SSL(BUSINESS.EMAIL_HOST)
    s.login(me, my_password)

    s.sendmail(me, msg["To"].split(","), msg.as_string())
    s.quit()


send_mail()
