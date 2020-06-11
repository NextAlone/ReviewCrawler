import os
import smtplib
from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, parseaddr, formataddr


def format_addr(address):
    """
    生成格式化头部
    :param address: 邮件地址
    :return: 格式化的邮件地址头部
    """
    name, addr = parseaddr(address)
    return formataddr((Header(name, 'utf-8').encode(), addr))


class EmailSender(object):
    def __init__(self, smtp_server, smtp_port=25, encoding="utf-8"):
        """
        初始化EmailSender类
        :param smtp_server: 邮件SMTP服务器地址。
        :param smtp_port:   邮箱端口地址，默认值为25。
        :param encoding:    邮件正文及附件的编码格式，默认为UTF-8.
        """
        self.server = smtp_server
        self.port = int(smtp_port)
        self.encoding = encoding
        self.from_addr = ''
        self.attachments = []
        # 创建SMTP实例
        self.smtp = smtplib.SMTP(self.server, self.port)

    def login(self, user, password):
        """
        登录到服务器。
        :param user: 邮箱用户名
        :param password: 邮箱密码或临时密钥
        """
        self.from_addr = user + "@" + ".".join(self.server.split(".")[1:])
        # 连接到服务器
        try:
            self.smtp.login(user, password)
            print('登录SMTP服务器成功。服务器：{0}:{1}。'.format(self.server, self.port))
        except Exception as e:
            print('登录SMTP服务器失败。错误信息：', e)

    def __add_attachment_file(self, filepath, filename, encoding=None):
        """
        添加邮件附件
        :param filepath: 邮件附件路径。
        :param filename:  邮件附件的文件名。
        :param encoding:  附件的编码。
        """
        # Check if the file is acceptable by the Filter
        if not encoding:
            encoding = self.encoding
        try:
            file = os.path.join(filepath, filename)
            attach = MIMEBase("application", "octet-stream")
            attach.set_payload(open(file, "rb").read())
            attach.add_header(
                "Content-Disposition",
                "attachment",
                filename=(
                    encoding,
                    "",
                    filename))
            encoders.encode_base64(attach)
            self.attachments.append(attach)
        except Exception as e:
            print('添加附件失败。错误信息：', filename, str(e))

    def send_email(
            self,
            subject,
            to_addrs,
            cc_addrs,
            content,
            subtype="plain",
            attachment=None,
            charset=None):
        """
        发送邮件。
        :param subject:    邮件主题。
        :param to_addrs:   收件人列表。
        :param cc_addrs:   抄送人列表。
        :param content:    邮件正文，格式可为文本或HTML，根据subtype选择。
        :param subtype:    内容格式，可为'plain'或'html'，默认为'plain'。
        :param attachment  邮件附件，包含附件路径及文件名，默认为空。
        :param charset:    邮件内容编码，默认为'None'，调用初始化的编码类型。
        :return: 发送成功返回True，否则返回False。
        """
        if attachment is None:
            attachment = []
        charset = charset if charset is not None else self.encoding

        # 设置邮件根信息
        msg_root = MIMEMultipart("related")
        msg_root["Subject"] = subject
        msg_root["From"] = format_addr(u'PythonCrawler <%s>' % self.from_addr)
        msg_root["To"] = ",".join(to_addrs)
        msg_root["CC"] = ",".join(cc_addrs)
        msg_root["Date"] = formatdate(localtime=True)
        msg_root.preamble = "This is a multi-part message in MIME format."

        # 将消息正文的纯文本和HTML封装为“替代”部分，使消息代理可以决定要显示的内容。
        msg_alt = MIMEMultipart("alternative")
        # 设置正文内容
        msg_txt = MIMEText(''.join(content), subtype.lower(), charset)
        msg_alt.attach(msg_txt)
        # 添加可变部分
        msg_root.attach(msg_alt)
        # 添加附件
        self.add_attachment_file(attachment)
        for attach in self.attachments:
            msg_root.attach(attach)
        # 拓展抄送人
        to_addrs.extend(cc_addrs)
        # 发送邮件
        try:
            self.smtp.sendmail(self.from_addr, to_addrs, msg_root.as_string())
        except Exception as e:
            print('邮件发送失败。错误信息：{0}'.format(e))

    def add_attachment_file(self, attachment):
        path = attachment[0]
        files = attachment[1]
        if not os.path.exists(path):
            raise Exception('附件路径不存在')
        if files:
            for file in files:
                self.__add_attachment_file(path, file)


def send(title, path, file_name_suffix):
    """
    :param title: 电影名称
    :param path:  文件路径
    :param file_name_suffix:  文件后缀列表
    """
    mail_host = 'smtp.163.com'
    mail_from = 'nextducts'
    mail_pass = 'EXBBVWLNKOQGIASN'
    mail_to = ['nextducts@163.com', '2463811949@qq.com', '1378099423@qq.com']
    mail_cc = ['1310252406@qq.com', 'love5212138@gmail.com']
    subject = "豆瓣电影抓取--" + title
    content = ['<html><body><h1>{0}</h1>'.format(subject), '</body></html>']
    attach_file_path = path
    attach_files = [str(title) + x for x in file_name_suffix]
    attach = [attach_file_path, attach_files]
    try:
        # 实例化EmailSender
        email_sender = EmailSender(mail_host)
        email_sender.login(mail_from, mail_pass)
        email_sender.send_email(
            subject,
            mail_to,
            mail_cc,
            content,
            'html',
            attach)
    except Exception as e:
        print('邮件发送出现未知错误。错误信息：', e)
    else:
        print('邮件发送成功。')
        return True
