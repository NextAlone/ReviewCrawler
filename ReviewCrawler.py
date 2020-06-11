import csv
import os
import random
import shutil
import time
from urllib.parse import urlencode

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import jieba
import numpy as np
import requests
from lxml import etree
from matplotlib import pyplot as plt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from snownlp import SnowNLP
from wordcloud import WordCloud

from CrawlerProcess import send

# 设置词云字体路径
WC_FONT_PATH = r'C:\Windows\Fonts\simhei.ttf'

session = requests.Session()
# 设置代理
proxies = {
    "http": "http://120.24.231.203:8080",
    # "http": "http://223.167.7.112:8060",
    "https": "http://223.243.4.51:4216",
}
# 设置头部
headers = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4164.4 Safari/537.36',
}


# 定义登录
def login():
    url = "https://accounts.douban.com/j/mobile/login/basic"
    data = {
        'name': '18501910988',
        'password': r'Q3aF3BiQvcr!vuP',
        'remember': 'false',
    }
    cookies = {
        'cookie': 'bid=iBxpSJYJUHM; __gads=ID=df4e600ad2ea16b3:T=1588037075:S=ALNI_MbdX7EPlcOyNNLXl3KlEAwzDW1hsQ; __utma=30149280.476129765.1588037078.1588037078.1588037078.1; __utmc=30149280; __utmz=30149280.1588037078.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); gr_user_id=7ffae438-179f-4c1e-8f40-830c44acb32c; _vwo_uuid_v2=DE151CB8C2F41E16D472D516641BEC938|e7a486aab194314932b78465aead15b2; viewed="26329916_2304817"; __yadk_uid=S0unLCOmj4lfHiznba5rU3JGimsx51qC; ll="118226"; push_noty_num=0; push_doumail_num=0; douban-profile-remind=1; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1591675008%2C%22https%3A%2F%2Fsearch.douban.com%2Fmovie%2Fsubject_search%3Fsearch_text%3D%25E6%25B5%2581%25E6%25B5%25AA%25E5%259C%25B0%25E7%2590%2583%22%5D; _pk_ses.100001.4cf6=*; dbcl2="197952164:C60grevUaZQ"; ck=ZjZN; _pk_id.100001.4cf6=3bd271c5fbad1e33.1591625554.7.1591675017.1591673070.; ap_v=0,6.0'}
    # 设置代理，从西刺免费代理网站上找出一个可用的代理IP
    user = session.post(url=url, headers=headers, data=data)
    # user = session.post(url=url, headers=headers, cookies=cookies)
    print(user.text)


class Spider:
    """
    爬虫类
    """

    def __init__(self):
        self.movie_url = None
        self.movie_id = None
        self.movie_name = None

    def spider_url(self, review_url):
        """
        根据URL查找。
        :param review_url:电影豆瓣URL
        """
        page = 0
        path = os.getcwd()
        fn = path + './Review/url-data.csv'
        with open(fn, 'w', encoding='utf_8_sig') as fp:
            wr = csv.writer(fp)
            wr.writerow(['Review'])
            while True:
                comment_url = review_url[:42] + 'comments'
                params = {
                    'start': page * 20,
                    'limit': 20,
                    'sort': 'new_score',
                    'status': 'P'
                }
                html = session.get(
                    url=comment_url,
                    params=params,
                    headers=headers,
                    proxies=proxies)
                page += 1
                print(
                    "开始爬取第{0}页***********************************************************************：".format(page))
                print(html.url)
                xpath_tree = etree.HTML(html.text)
                if page == 0:
                    self.movie_name = str(xpath_tree.xpath(
                        '//*[@id="wrapper"]/div[@id="content"]/h1')[0].text).strip(' ').replace('短评', '').replace(' ',
                                                                                                                  '-')
                comment_divs = xpath_tree.xpath('//*[@id="comments"]/div')
                if len(comment_divs) > 2:
                    # 获取每一条评论的具体内容
                    for comment_div in comment_divs:
                        comment = comment_div.xpath('./div[2]/p/span/text()')
                        if len(comment) > 0:
                            # print(comment[0])
                            wr.writerow([comment[0]])
                    time.sleep(int(random.choice([0.5, 0.2, 0.3])))
                else:
                    print("大约共{0}页评论".format(page - 1))
                    break
        new_filename = path + './Review/' + self.movie_name + '-data.csv'
        shutil.move(fn, new_filename)

    def spider_id(self, review_id):
        """
        根据id查找
        :param:电影豆瓣ID
        """
        page = 0
        path = os.getcwd()
        fn = path + './Review/' + review_id + '-data.csv'
        with open(fn, 'w', encoding='utf_8_sig') as fp:
            wr = csv.writer(fp)
            wr.writerow(['Review'])
            while True:
                move_url = 'https://movie.douban.com/subject/' + review_id + '/comments?'
                params = {
                    'start': page * 20,
                    'limit': 20,
                    'sort': 'new_score',
                    'status': 'P'
                }
                html = session.get(
                    url=move_url,
                    params=params,
                    headers=headers,
                    # proxies=proxies
                )
                print(html.url)
                page += 1
                print(
                    "开始爬取第{0}页***********************************************************************：".format(page))
                print(html.url)
                xpath_tree = etree.HTML(html.text)
                if page == 1:
                    self.movie_name = str(xpath_tree.xpath(
                        '//*[@id="wrapper"]/div[@id="content"]/h1')[0].text).strip(' ').replace('短评', '').replace(' ',
                                                                                                                  '-')
                comment_divs = xpath_tree.xpath('//*[@id="comments"]/div')
                if len(comment_divs) > 2:
                    # 获取每一条评论的具体内容
                    for comment_div in comment_divs:
                        comment = comment_div.xpath('./div[2]/p/span/text()')
                        if len(comment) > 0:
                            # print(comment[0])
                            wr.writerow([comment[0]])
                    time.sleep(int(random.choice([0.5, 0.2, 0.3])))
                else:
                    print("大约共{0}页评论".format(page - 1))
                    break
        new_filename = path + './Review/' + self.movie_name + '-data.csv'
        shutil.move(fn, new_filename)

    def spider_name(self, review_name):
        """
        根据名称查找
        :param 电影名称（模糊）。
        """
        params = urlencode({'search_text': review_name})
        move_url = 'https://movie.douban.com/subject_search'
        html = requests.get(
            url=move_url,
            headers=headers,
            params=params,
            # proxies=proxies
        )
        # 利用selenium模拟浏览器，找到电影的url
        chrome_options = Options()
        # chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_argument('--headless')
        chrome_options.add_argument(
            'User-Agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15"')
        # chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument('--disable-dev-shm-usage')
        drive = webdriver.Chrome(
            r'C:\Program Files (x86)\Google\Chrome Dev\Application\chromedriver.exe',
            options=chrome_options)
        drive.get(html.url)
        print(html.url)
        first_result = drive.find_element_by_xpath(
            '//div[@id="root"]/div/div[2]/div[1]/div[1]/div/div[1]/div/div[1]/a').get_attribute('href')
        page = 0
        # 每次写入前清空文件
        path = os.getcwd()
        fn = path + './Review/' + review_name + '-data.csv'
        with open(fn, 'w', encoding='utf_8_sig') as fp:
            wr = csv.writer(fp)
            wr.writerow(['Review'])
            while True:
                move_url = first_result + '/comments?'
                params = {
                    'start': page * 20,
                    'limit': 20,
                    'sort': 'new_score',
                    'status': 'P'
                }
                html = session.get(
                    move_url,
                    params=params,
                    headers=headers,
                    timeout=3)
                page += 1
                print(
                    "开始爬取第{0}页***********************************************************************：".format(page))
                print(html.url)
                xpath_tree = etree.HTML(html.text)
                if page == 1:
                    self.movie_name = str(
                        xpath_tree.xpath('//*[@id="wrapper"]/div[@id="content"]/h1')[0].text).replace(
                        '短评', '').strip(' ').replace(
                        ' ', '-')
                comment_divs = xpath_tree.xpath('//*[@id="comments"]/div')
                if len(comment_divs) > 2:
                    # 获取每一条评论的具体内容
                    for comment_div in comment_divs:
                        comment = comment_div.xpath('./div[2]/p/span/text()')
                        if len(comment) > 0:
                            # print(comment[0])
                            wr.writerow([comment[0]])
                    time.sleep(int(random.choice([0.5, 0.2, 0.3])))
                else:
                    print("大约共{0}页评论".format(page - 1))
                    break
        new_filename = path + './Review/' + self.movie_name + '-data.csv'
        shutil.move(fn, new_filename)

    def spider_kind(self):
        """
        设置搜索类型
        """
        try:
            kind = int(input("请选择搜索类型：1.根据电影链接 2.根据电影id 3.根据电影名："))
            if kind == 1:
                self.movie_url = input("请输入电影链接:")
                if self.movie_url is None:
                    raise RuntimeError('电影链接为空')
                self.spider_url(self.movie_url)
            elif kind == 2:
                self.movie_id = input("请输入电影id:")
                if self.movie_id is None:
                    raise RuntimeError('电影id为空')
                self.spider_id(self.movie_id)
            elif kind == 3:
                self.movie_name = input("请输入电影名:")
                if self.movie_name is None:
                    raise RuntimeError('电影名为空')
                self.spider_name(self.movie_name)
            else:
                print("搜索类型输入错误！")
                print('*' * 50)
                self.spider_kind()
        except Exception as exception:
            if 'Unable to locate element' in str(exception):
                print('IP封禁或无此对象：', exception)
            elif 'HTTPSConnectionPool' in str(exception):
                print('连接尝试失败：', exception)
            else:
                print("信息输入不全或错误：", exception)
            print('*' * 50)
            self.spider_kind()


def cut_word(movie_name):
    """
    定义词汇分割
    :param movie_name: 电影名称。
    :return:返回分割后的评论列表。
    """
    file_path = r'./Review/' + movie_name + '-data.csv'
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        # 读取文件里面的全部内容
        comment_txt = file.read()
        # 使用jieba进行分割
        word_list = jieba.cut(comment_txt)
        print('分割评论。')
        # print('***********', word_list)
        word_list_cut = "/".join(word_list)
        # print(word_list_cut)
        return word_list_cut


# 生成词云蒙版
def create_word_cloud_mask(movie_name):
    """
    生成词云蒙版
    :param movie_name: 电影名称
    :return: 返回生成的词云模板
    """
    text = movie_name
    im = PIL.Image.new("RGB", (len(text) * 400 + 50, 450), (255, 255, 255))
    dr = PIL.ImageDraw.Draw(im)
    font = PIL.ImageFont.truetype(os.path.join("fonts", "STXINGKA.TTF"), 400)
    dr.text((25, 25), text, font=font, fill="#000000")
    return im


def create_word_cloud(movie_name):
    """
    创建词云
    :param movie_name: 电影名称。
    """
    # 设置词云形状图片,numpy+PIL方式读取图片
    wc_mask = np.array(create_word_cloud_mask(movie_name))
    # 数据清洗词列表
    stop_words = {
        '就是',
        '不是',
        '但是',
        '还是',
        '只是',
        '这样',
        '这个',
        '一个',
        '什么',
        '电影',
        '没有'}
    # 设置词云的一些配置，如：字体，背景色，词云形状，大小,生成词云对象
    wc = WordCloud(
        mask=wc_mask,
        background_color="white",
        stopwords=stop_words,
        max_words=len(movie_name) * 50,
        scale=8,
        max_font_size=50,
        random_state=42,
        font_path=WC_FONT_PATH)
    # 生成词云
    wc.generate(cut_word(movie_name))
    # 在只设置mask的情况下,你将会得到一个拥有图片形状的词云
    # 开始画图
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    plt.imshow(wc, interpolation="bilinear")
    # 为云图去掉坐标轴
    plt.axis("off")
    plt.figure()
    img = r'./Review/' + movie_name + '-词云.png'
    # plt.show()
    wc.to_file(img)
    print('文件已保存：', img)


def sentiment_show(movie_name):
    """
     生成情感分析
    :param movie_name:
    """
    file_path = r'./Review/' + movie_name + '-data.csv'
    f = open(file_path, 'r', encoding='UTF-8')
    review_list = f.readlines()
    sentiments_list = []
    for i in review_list:
        s = SnowNLP(i)
        sentiments_list.append(s.sentiments)
    print(sentiments_list)
    print(len(sentiments_list))
    plt.hist(sentiments_list, bins=10, facecolor='g')
    plt.xlabel('情感概率')
    plt.ylabel('数量')
    plt.title('情感分析-' + movie_name)
    img = r'./Review/' + movie_name + '-情感分析.png'
    fig = plt.gcf()
    # plt.show()
    fig.savefig(img)
    print('文件已保存：', img)


if __name__ == '__main__':
    spider = Spider()
    try:
        # login()
        spider.spider_kind()
    except Exception as e:
        if 'Unable to locate element' in str(e):
            print('IP封禁或无此对象：', e)
        else:
            print('查询错误：', e)
    else:
        try:
            create_word_cloud(spider.movie_name)
            sentiment_show(spider.movie_name)
            file_name_suffix = ['-词云.png', '-情感分析.png']
            send(spider.movie_name, './Review', file_name_suffix)
        except Exception as e:
            print('创建词云与情感分析出错。', e)
