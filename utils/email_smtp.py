import subprocess
from conf import settings
from utils import email_template


def mail_send(send_to, template_name, template_var):
    if send_to:
        send_to += 'aaron.bu@m1om.me'
        print(send_to)
        template_obj = getattr(email_template, template_name)
        mail_title, mail_content = template_obj(**template_var)
        send_mail = subprocess.Popen([settings.pyenv, './utils/smtp.py', send_to, mail_title, mail_content])

if __name__ == '__main__':
    mail_send('aaron@monaco1.ph', 'asset_apply_create', {'title': ['我的测试任务'], 'content': ['aaron.bu', 4]})