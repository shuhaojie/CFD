import os
import sys
import smtplib
from pathlib import Path
from email.mime.base import MIMEBase
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

from utils.constant import BUSINESS


def send_mail(task_status='SUCCESS'):
    # query = await Uknow.filter(task_id=task_id).first()
    # order_id = query.order_id
    # send_to = get_email_by_order_id(order_id)
    send_to = 'shuhaojie@unionstrongtech.com'
    send_from = BUSINESS.EMAIL_FROM
    print(send_from)
    if task_status == 'SUCCESS':
        subject = 'CFD任务成功'
        message = '附件为encas文件'
    else:
        subject = 'CFD任务失败'
        message = '附件为日志文件'
    # file_path = r'C:\workspaces\CFD\data\ensight_result.encas'
    file_path = '/workspaces/data/archive/20230208172439001/ensight_result.encas'
    server = BUSINESS.EMAIL_HOST
    port = BUSINESS.EMAIL_PORT
    username = BUSINESS.EMAIL_USER
    password = BUSINESS.EMAIL_PASSWORD
    use_tls = BUSINESS.EMAIL_USE_SSL
    # print(server, port, username, password, use_tls)
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(message))

    part = MIMEBase('application', "octet-stream")
    with open(file_path, 'rb') as file:
        part.set_payload(file.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition',
                    'attachment; filename={}'.format(Path(file_path).name))
    msg.attach(part)

    smtp = smtplib.SMTP_SSL()
    smtp.connect(server, port)
    smtp.login(username, password)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.quit()


def new_send_email():
    # skipped your comments for readability
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    me = BUSINESS.EMAIL_FROM
    my_password = BUSINESS.EMAIL_PASSWORD
    you = "shuhaojie@unionstrongtech.com"

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Alert"
    msg['From'] = me
    msg['To'] = you

    html = '<html><body><p>Hi, I have the following alerts for you!</p></body></html>'
    part2 = MIMEText(html, 'html')

    msg.attach(part2)

    # Send the message via gmail's regular server, over SSL - passwords are being sent, afterall
    s = smtplib.SMTP_SSL(BUSINESS.EMAIL_HOST)
    # uncomment if interested in the actual smtp conversation
    # s.set_debuglevel(1)
    # do the smtp auth; sends ehlo if it hasn't been sent already
    s.login(me, my_password)

    s.sendmail(me, you, msg.as_string())
    s.quit()


new_send_email()
