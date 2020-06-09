import random
import time
from urllib.parse import urlencode

import jieba
import numpy as np
import requests
from PIL import Image
from lxml import etree
from matplotlib import pyplot as plt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from snownlp import SnowNLP
from wordcloud import WordCloud

# 设置词云路径
WC_FONT_PATH = r'C:\Windows\Fonts\simhei.ttf'

session = requests.Session()
proxies = {
    "http": "http://223.167.7.112:8060",
}
headers = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4164.4 Safari/537.36',
}


def login():
    url = "https://accounts.douban.com/j/mobile/login/basic"
    data = {
        'name': '豆瓣账号',
        'password': '密码',
        'remember': 'false'
    }
    # 设置代理，从西刺免费代理网站上找出一个可用的代理IP
    user = session.post(url=url, headers=headers, data=data, proxies=proxies)
    print(user.text)


class Spider:
    @staticmethod
    def spider_url(review_url):
        page = 0
        f = open('result.txt', 'a+', encoding="utf-8")
        f.seek(0)
        f.truncate()
        while True:
            comment_url = review_url[:42] + 'comments'
            params = {
                'start': page * 20,
                'limit': 20,
                'sort': 'new_score',
                'status': 'P'
            }
            html = session.get(url=comment_url, params=params, proxies=proxies)
            page += 1
            print(
                "开始爬取第{0}页***********************************************************************：".format(page))
            print(html.url)
            xpath_tree = etree.HTML(html.text)
            comment_divs = xpath_tree.xpath('//*[@id="comments"]/div')
            if len(comment_divs) > 2:
                # 获取每一条评论的具体内容
                for comment_div in comment_divs:
                    comment = comment_div.xpath('./div[2]/p/span/text()')
                    if len(comment) > 0:
                        print(comment[0])
                        f.write(comment[0] + '\n')
                time.sleep(int(random.choice([0.5, 0.2, 0.3])))
            else:
                f.close()
                print("大约共{0}页评论".format(page - 1))
                break

    @staticmethod
    def spider_id(review_id):
        page = 0
        f = open('result.txt', 'a+', encoding='utf-8')
        f.seek(0)
        f.truncate()
        while True:
            move_url = 'https://movie.douban.com/subject/' + review_id + '/comments?'
            params = {
                'start': page * 20,
                'limit': 20,
                'sort': 'new_score',
                'status': 'P'
            }
            html = session.get(url=move_url, params=params, proxies=proxies)
            print(html.url)
            page += 1
            print(
                "开始爬取第{0}页***********************************************************************：".format(page))
            print(html.url)
            xpath_tree = etree.HTML(html.text)
            comment_divs = xpath_tree.xpath('//*[@id="comments"]/div')
            if len(comment_divs) > 2:
                # 获取每一条评论的具体内容
                for comment_div in comment_divs:
                    comment = comment_div.xpath('./div[2]/p/span/text()')
                    if len(comment) > 0:
                        print(comment[0])
                        f.write(comment[0] + '\n')
                time.sleep(int(random.choice([0.5, 0.2, 0.3])))
            else:
                f.close()
                print("大约共{0}页评论".format(page - 1))

    @staticmethod
    def spider_name(review_name):
        params = urlencode({'search_text': review_name})
        move_url = 'https://movie.douban.com/subject_search'
        html = requests.get(
            url=move_url,
            headers=headers,
            params=params,
            proxies=proxies)
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
        # first_result = 'https://movie.douban.com/subject/26266893/'
        page = 0
        # 每次写入前清空文件
        f = open('result.txt', 'a+', encoding=html.encoding)
        f.seek(0)
        f.truncate()
        while True:
            move_url = first_result + '/comments?'
            params = {
                'start': page * 20,
                'limit': 20,
                'sort': 'new_score',
                'status': 'P'
            }
            html = requests.get(
                move_url,
                params=params,
                headers=headers,
                timeout=3)
            page += 1
            print(
                "开始爬取第{0}页***********************************************************************：".format(page))
            print(html.url)
            xpath_tree = etree.HTML(html.text)
            comment_divs = xpath_tree.xpath('//*[@id="comments"]/div')
            if len(comment_divs) > 2:
                # 获取每一条评论的具体内容
                for comment_div in comment_divs:
                    comment = comment_div.xpath('./div[2]/p/span/text()')
                    if len(comment) > 0:
                        print(comment[0])
                        f.write(comment[0] + '\n')
                time.sleep(int(random.choice([0.5, 0.2, 0.3])))
            else:
                f.close()
                print("大约共{0}页评论".format(page - 1))
                break


# 定义搜索类型
def spider_kind():
    kind = int(input("请选择搜索类型：1.根据电影链接 2.根据电影id 3.根据电影名："))
    if kind == 1:
        movie_url = input("请输入电影链接:")
        Spider.spider_url(movie_url)
    elif kind == 2:
        movie_id = input("请输入电影id:")
        Spider.spider_id(movie_id)
    elif kind == 3:
        movie_name = input("请输入电影名:")
        Spider.spider_name(movie_name)
    else:
        print("sorry,输入错误！")


def cut_word():
    with open('result.txt', 'r', encoding='utf-8') as file:
        # 读取文件里面的全部内容
        comment_txt = file.read()
        # 使用jieba进行分割
        word_list = jieba.cut(comment_txt)
        print('***********', word_list)
        word_list_cut = "/".join(word_list)
        print(word_list_cut)
        return word_list_cut


def create_word_cloud():
    # 设置词云形状图片,numpy+PIL方式读取图片
    wc_mask = np.array(Image.open('WordCloud.jpg'))
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
        max_words=50,
        scale=4,
        max_font_size=50,
        random_state=42,
        font_path=WC_FONT_PATH)
    # 生成词云
    wc.generate(cut_word())

    # 在只设置mask的情况下,你将会得到一个拥有图片形状的词云
    # 开始画图
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    plt.imshow(wc, interpolation="bilinear")
    # 为云图去掉坐标轴
    plt.axis("off")
    plt.figure()
    img = './Review/Cloud.png'
    plt.savefig(img)
    plt.show()


def data_show():
    f = open('result.txt', 'r', encoding='UTF-8')
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
    plt.title('情感分析')
    plt.show()
    img = './Review/sentiments.png'
    plt.savefig(img)


if __name__ == '__main__':
    login()
    spider_kind()
    create_word_cloud()
    data_show()