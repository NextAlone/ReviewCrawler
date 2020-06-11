import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr


# 格式化邮件地址
def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


mail_host = 'smtp.163.com'
mail_from = 'nextducts@163.com'
mail_pass = 'EXBBVWLNKOQGIASN'
mail_to = ['love5212138@gmail.com', '1378099423@qq.com']


def send_mail(title):
    # 构造一个MIMEMultipart对象代表邮件本身
    # 设置email信息
    # 邮件内容设置
    message = MIMEMultipart()
    message.attach(MIMEText('啦啦啦' + title, 'plain', 'utf-8'))
    # 邮件主题
    message['Subject'] = 'Python--' + title
    # 发送方信息
    message['From'] = _format_addr(u'NextAlone <%s>' % mail_from)
    # 接受方信息
    message['To'] = ','.join(mail_to)

    # 登录并发送邮件
    try:
        smpt = smtplib.SMTP()
        # 连接到服务器
        smpt.connect(mail_host, 25)
        # 登录到服务器
        smpt.login(mail_from, mail_pass)
        # 发送
        smpt.sendmail(mail_from, mail_to, message.as_string())
        # 退出
        smpt.quit()
        print('发送成功。')
    except smtplib.SMTPException as e:
        print('发送失败：', e)  # 打印错误
    except Exception as e:
        print('发送失败：', e)  # 打印错误
