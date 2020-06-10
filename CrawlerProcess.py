import codecs
import smtplib
from base64 import b64encode, b64decode
from email.header import Header
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr


def encode(s, name="utf-8", *args, **kwargs):
    if name == 'base64':
        if isinstance(s, str):
            s = bytearray(s, 'utf-8')
        return b64encode(s).decode('utf-8').strip()
    codec = codecs.lookup(name)
    rv, length = codec.encode(s, *args, **kwargs)
    if not isinstance(rv, (str, bytes, bytearray)):
        raise TypeError('Not a string or byte codec')
    return rv


def decode(s, name="utf-8", *args, **kwargs):
    if name == 'base64':
        try:
            return bytearray(b64decode(s)).decode('utf-8')
        except:
            pass
    codec = codecs.lookup(name)
    rv, length = codec.decode(s, *args, **kwargs)
    if not isinstance(rv, (str, bytes, bytearray)):
        raise TypeError('Not a string or byte codec')
    return rv


# 格式化邮件地址
def format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def sent_mail(mail_body, image):
    smtp_server = 'smtp.163.com'
    mail_from = 'nextducts@163.com'
    mail_pass = 'EXBBVWLNKOQGIASN'
    mail_to = ['1378099423@qq.com', '2463811949@qq.com']
    # 构造一个MIMEMultipart对象代表邮件本身
    msg = MIMEMultipart()
    # Header对中文进行转码
    msg['From'] = format_addr('Ducts <%s>' % mail_from).encode()
    msg['To'] = ','.join(mail_to)
    msg['Subject'] = Header('PythonTest', 'utf-8').encode()
    # msg.attach(MIMEText(mail_body, 'html', 'utf-8'))
    # 二进制模式读取图片
    # with open(image, 'rb') as f:
    #     msg_image = MIMEImage(f.read())
    # # 定义图片ID
    # msg_image.add_header('Content-ID', '<image1>')
    # msg.attach(msg_image)
    try:
        s = smtplib.SMTP()
        s.connect(smtp_server, "25")
        s.login(mail_from, mail_pass)
        s.sendmail(mail_from, mail_to, msg.as_string())  # as_string()把MIMEText对象变成str
        s.quit()
        print('发送成功。')
    except smtplib.SMTPException as e:
        print('发送失败：', e)  # 打印错误
    except Exception as e:
        print('发送失败：', e)  # 打印错误


if __name__ == "__main__":
    body = """
    <h1>测试图片</h1>
    <img src="cid:image1"/>    # 引用图片
    """
    sent_mail(body, 'WordCloud.jpg')
