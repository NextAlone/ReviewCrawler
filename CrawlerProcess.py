import smtplib
from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
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
mail_to = ['nextducts@163.com', '2463811949@qq.com', '1378099423@qq.com']


def send_mail(title):
    # 构造一个MIMEMultipart对象代表邮件本身
    # 设置email信息
    # 邮件内容设置
    msg = MIMEMultipart()
    txt = '''<html>
    <body><h1>{0}</h1>
    <p><img style="width:400px" src="cid:image1"></p>
    <p><img style="width:400px" src="cid:image2"></p></body></html>'''.format(title)
    msg.attach(MIMEText(txt, 'html', 'utf-8'))
    # msg = MIMEText('<html><h1>{0}</h1></html>', 'html', 'utf-8')
    # 邮件主题
    msg['Subject'] = 'Python--' + title
    # 发送方信息
    msg['From'] = _format_addr(u'NextAlone <%s>' % mail_from)
    # 接受方信息
    msg['To'] = ','.join(mail_to)
    # 添加邮件附件
    with open('./Review/' + title + '-词云.png', 'rb') as fp:
        img = MIMEBase('image', 'png', filename=title + '-词云.png')
        img.add_header(
            'Content-Disposition',
            'attachment',
            filename=title + '-词云.png')
        img.add_header('Content-ID', '<image1>')
        img.add_header('X-Attachment-Id', '0')
        img.set_payload(fp.read())
        encoders.encode_base64(img)
        msg.attach(img)
    with open('./Review/' + title + '-情感分析.png', 'rb') as fp:
        img = MIMEBase('image', 'png', filename=title + '-情感分析.png')
        img.add_header(
            'Content-Disposition',
            'attachment',
            filename=title + '-情感分析.png')
        img.add_header('Content-ID', '<image2>')
        img.add_header('X-Attachment-Id', '1')
        img.set_payload(fp.read())
        encoders.encode_base64(img)
        msg.attach(img)
    # 登录并发送邮件
    try:
        smpt = smtplib.SMTP()
        # 连接到服务器
        smpt.connect(mail_host, 25)
        # 登录到服务器
        smpt.login(mail_from, mail_pass)
        # 发送
        smpt.sendmail(mail_from, mail_to, msg.as_string())
        # 退出
        smpt.quit()
        print('发送成功。')
    except smtplib.SMTPException as e:
        print('发送失败：', e)  # 打印错误
    except Exception as e:
        print('发送失败：', e)  # 打印错误
