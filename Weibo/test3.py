# coding : UTF-8
import os
import requests
import csv
import random
import time
import datetime
import ftplib
import threading
import shutil
import sys
# from cProfile import Profile
from hdfs.client import *
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
from fake_useragent import UserAgent

#重写线程类 可以有返回值
class MyThread(threading.Thread):
    def __init__(self, func, args=()):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None

#把控制台输出到txt
class Logger(object):
    def __init__(self, fileN="Default.log"):
        self.terminal = sys.stdout
        self.log = open(fileN, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass

#控制台日志
sys.stdout = Logger("E:\\GitHub\\Python\\text_log_2.txt")

ua = UserAgent(use_cache_server=False)

# 伪装浏览器
request_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'DNT': '1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/67.0.3396.62 Safari/537.36'
    # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
    #               'Chrome/63.0.3239.132 Safari/537.36'
}

# IP池
proxy = [
    '61.135.217.7:80',
    '222.182.121.246:8118',
    '118.190.95.35:9001',
    '61.184.109.33;61320',
    '116.77.204.2:80',
    '60.216.101.46:59351',
    '183.159.90.14:18118',
    '112.98.126.100:41578',
    '180.168.13.26:8000',
    '180.118.241.94:61234',
    '175.148.78.174:1133',
    '115.46.73.58:8123',
    '175.155.24.39:808',
    '42.48.118.106:50038',
    '110.86.15.46:58945',
    '175.155.24.41:808',
    '59.32.37.112:61234',
    '171.38.79.36:8123',
    '122.115.78.240:38157',
    '116.192.171.51:48565',
    '61.138.33.20:808',
    '115.151.2.154:808',
    '175.175.219.97:1133',
    '59.32.37.82:8010',
    '171.37.162.104:8123',
    '115.46.71.44:8123',
    '110.73.6.199:8123',
    '182.88.135.96:8123',
    '49.85.4.155:43193',
    '60.179.40.16:808',
    '36.99.207.234:35618',
    '171.12.165.136:808',
    '49.85.3.191:30718',
    '123.161.152.173:22694',
    '119.5.1.21:808',
    '111.160.236.84:39692',
    '221.214.180.122:33190',
    '175.155.24.48:808',
    '115.29.200.195:808',
    '180.122.150.247:26055',
    '49.85.7.132:21026',
    '222.186.45.132:61374',
    '219.136.252.124:53281',
    '1.195.60.132:8118',
    '182.88.165.7:8123',
    '124.235.181.175:80',
    '180.118.241.187:808',
    '115.46.72.171:8123',
    '171.37.159.106:8123',
    '114.225.168.235:53128',
    '111.72.154.240:53128',
    '59.32.37.28:8010',
    '175.155.24.57:808',
    '59.32.37.134:8010',
    '119.5.0.18:808',
    '122.237.104.9:80',
    '114.225.171.173:53128',
    '175.148.75.246:1133',
    '119.5.1.33:808',
    '182.88.128.227:8123',
    '118.249.49.12:8118',
    '115.46.68.69:8123',
    '119.5.1.42:808',
    '171.37.158.178:8123',
    '121.31.176.201:8123',
    '121.31.193.254:8123',
    '119.5.1.51:808',
    '182.88.135.131:8123',
    '119.5.0.4:808',
    '121.31.156.98:8123',
    '210.72.14.142:80',
    '124.113.251.3:8010',
    '58.49.15.94:42821',
    '115.46.97.85:8123',
    '123.162.168.192:40274',
    '115.46.67.89:8123',
    '182.91.67.224:8123',
    '202.103.12.30:60850',
    '59.32.37.151:3128',
    '61.157.206.186:59007'
]

# 连接hdfs
client = Client("http://10.13.0.80:9870/", root="/", timeout=10000, session=False)

csv_limit = 1000
file_path = 'E:\\GitHub\\Python\\test4'#写入数据目录
upload_file_path='E:\\GitHub\\Python\\upload'#上传目录地址
#url字典
url = {
    # 'home_page':'https://s.weibo.com/weibo?q=%(keyword)s&typeall=1&suball=1&Refer=g&page=1',

    'home_page':'https://s.weibo.com/weibo?q=%(keyword)s&typeall=1&suball=1&timescope=custom:%(start_data)s:%(end_data)s&Refer=g&page=1',

    'page_by_lastdata':'https://s.weibo.com/weibo?q=%(keyword)s&typeall=1&suball=1&'
                         'timescope=custom:%(start_data)s:'
                         '%(dateend)s&Refer=g&page=1',
    'page_by_hour':'https://s.weibo.com/weibo?q=%(keyword)s&typeall=1&suball=1&timescope'
                   '=custom:%(start_time)s-%(hours)d:%(start_time)s-%(hours+1)d&Refer=g&page=1',
    'page_after_hour':'https://s.weibo.com/weibo?q=%(keyword)s&typeall=1&suball=1&'
                                'timescope=custom:%(start_data)s:'
                                '%(start_time)s-0&Refer=g&page=1'
}


# 获取html源文件方法
def get_html(url):
    a = random.randint(0,79)
    proxies =proxy[a]
    # 超时时间
    timeout = random.choice(range(80, 180))
    request_headers.update({'User-Agent': ua.chrome})
    while True:
        try:
            rep = requests.get(url, headers=request_headers, timeout=timeout, proxies={"http":proxies})
            rep.encoding = 'UTF-8'
            break
        except Exception as e:
            print('get_html ERROR:', e)
            time.sleep(random.choice(range(5, 15)))
    return rep.text


# 查找页面数据
def lookup_data(html_text):
    today_date = datetime.date.today()
    final = []
    target = SoupStrainer('div', {'class': 'card-wrap'})
    bs = BeautifulSoup(html_text, "html.parser", parse_only=target)
    # 进入微博 判断div有mid
    data = bs.find_all('div', mid=True)
    # print('当前页面含有mid数'+str(len(data)))
    for data_info in data:
        try:
            temp = []
            # 获取PostID
            try:
                PostID = data_info['mid']
            except Exception as e:
                print('PostID为空',e)
                PostID = 'null'
            # 获取UserID
            try:
                user_info = data_info.find('div', {'class': 'info'}).find_all('a', {'class': 'name'})
                UserID = user_info[0]['href'].split('/')[-1].split('?')[0]
            except Exception as e:
                print('UserID为空',e)
                UserID = 'null'


            # 获取PostFrom PostTime CreateTime
            try:
                from_info = data_info.find('p', {'class': 'from'}).find_all('a')
                PostTime = from_info[0].string.strip()
                if len(from_info) > 1:
                    PostFrom = from_info[1].string
                else:
                    PostFrom = 'null'
            except Exception as e:
                print('PostFrom PostTime为空',e)
                PostTime = 'null'
                PostFrom = 'null'


            # 获取ForwardCount CommentCount LikeCount
            try:
                count_info = data_info.find('div', {'class': 'card-act'}).find_all('li')
                ForwardCount = count_info[1].find('a').string[3:]
                if ForwardCount == '':
                    ForwardCount = '0'
                CommentCount = count_info[2].find('a').string[3:]
                if CommentCount == '':
                    CommentCount = '0'
                LikeCount = count_info[3].find('em').string
                if LikeCount == None:
                    LikeCount = '0'
            except Exception as e:
                print('ForwardCount CommentCount LikeCount为空', e)
                ForwardCount = '0'
                CommentCount = '0'
                LikeCount = '0'

            # 获取Content
            try:
                txt_count = data_info.find_all('p', {'class': 'txt'})
                # 判断是否转发的微博
                forward_count = data_info.find_all('div', {'class': 'card-comment'})

                # 有全文 无转发 或 有全文 有转发
                if (len(txt_count) > 1 and len(forward_count) == 0) or (len(txt_count) > 1 and len(forward_count) == 1):
                    content = data_info.find_all('p', {'class': 'txt'})
                    Content = content[1].get_text().strip()
                else:
                    content = data_info.find_all('p', {'class': 'txt'})
                    Content = content[0].get_text().strip()
            except Exception as e:
                print('Content为空',e)
                Content = 'null'

            # 获取有转发的ForwardFromUserID ForwardFromPostID
            try:
                if len(forward_count) == 1:
                    forward = data_info.find('ul', {'class': 'act s-fr'}).find_all('a')
                    ForwardFromUserID = forward[1]['href'].split('/')[-2].split('/')[-1]
                    ForwardFromPostID = forward[2]['action-data'].split('=')[-1]
                else:
                    ForwardFromUserID = 'null'
                    ForwardFromPostID = 'null'
            except Exception as e:
                print('ForwardFrom为空',e)
                ForwardFromUserID = 'null'
                ForwardFromPostID = 'null'

            # 获取Tags
            try:
                tag_info = txt_count
                Tags = []
                tag_a = tag_info[0].find_all('a')
                if len(tag_a) > 0:
                    for tag in tag_a:
                        if 'http://s' in tag['href']:
                            Tags.append(tag.get_text())
                    if Tags == []:
                        Tags = 'null'
                else:
                    Tags = 'null'
            except Exception as e:
                print('Tags为空',e)
                Tags = 'null'

            # 获取Urls 有视频的没有urls
            # 判断是否有视频
            videos_count = data_info.find_all('div', {'class': 'thumbnail'})
            url_info = txt_count
            urls = []
            # 有全文
            if len(videos_count) == 0 and len(txt_count) > 1 and len(forward_count) == 0:
                url_a = url_info[1].find_all('a')
                if len(url_a) > 0:
                    for url in url_a:
                        if 'http://t' in url['href']:
                            urls.append(url['href'])
                    if urls == []:
                        urls = 'null'
                else:
                    urls = 'null'
            # 无全文
            elif len(videos_count) == 0 and len(txt_count) == 1 and len(forward_count) == 0:
                url_a = url_info[0].find_all('a')
                if len(url_a) > 0:
                    for url in url_a:
                        if 'http://t' in url['href']:
                            urls.append(url['href'])
                    if urls == []:
                        urls = 'null'
                else:
                    urls = 'null'
            else:
                urls = 'null'

            # 获取Pics 转发的图片不算
            # 判断是否有图片
            m3_count = data_info.find_all('ul', {'class': 'm3'})
            if len(forward_count) == 0 and len(m3_count) == 1:
                pic = data_info.find('ul', {'class': 'm3'}).find_all('img')
                Pics = []
                for p in pic:
                    pics = p['src']
                    Pics.append(pics)
            else:
                Pics = 'null'

            # 获取Videos
            try:
                if len(videos_count) == 1 and len(forward_count) == 0:
                    video = videos_count[0].find('a')['action-data'].split('short_url=')[-1].split('&')[-8]
                    Videos = video.replace('%3A', ':').replace('%2F', '/')
                else:
                    Videos = 'null'
            except Exception as e:  # 如果没有 则置空
                Videos = 'null'
                pass

            temp.append(PostID)
            temp.append(UserID)
            temp.append(PostTime)
            temp.append(PostFrom)
            temp.append(ForwardCount)
            temp.append(CommentCount)
            temp.append(LikeCount)
            temp.append(Content)
            temp.append(ForwardFromUserID)
            temp.append(ForwardFromPostID)
            temp.append(Pics)
            temp.append(Videos)
            temp.append(Tags)
            temp.append(urls)
            temp.append(today_date)

            final.append(temp)

        except Exception as e:
            print('lookup_data: ', e)
    return final


# 保存数据
def save_data(data, name):
    file_name = name
    try:
        # encoding = 'utf-8'
        with open(file_name, 'a', errors='ignore', newline='') as f:
            f_csv = csv.writer(f)
            f_csv.writerows(data)
    except Exception as e:
        print('save_data:', e)


# 获取总页数
def get_all_page(html_text):
    target = SoupStrainer('div', {'class': 'm-page'})
    bs = BeautifulSoup(html_text, "html.parser", parse_only=target)
    ul = bs.find('ul', {'class': 's-scroll'})
    if ul != None:
        a = ul.find_all('a')
        last = a[-1].string[1:-1]
    else:
        last = '1'
    return last


# 判断当前页面有没有内容
def page_content(html_text):
    target = SoupStrainer('div', {'class': 'card-wrap'})
    bs = BeautifulSoup(html_text, "html.parser", parse_only=target)
    if bs.find('div', {'class': 'card card-no-result s-pt20b40'}):
        print('该页为空 跳过')
        return True
    else:
        return False


# 获取第一条微博的时间
def start_date(html_text):
    target = SoupStrainer('div', {'class': 'content'})
    bs = BeautifulSoup(html_text, "html.parser", parse_only=target)
    content = bs.find_all('div', {'class': 'content'})
    start_from = content[0].find_all('p', {'class': 'from'})
    a = start_from[-1].find_all('a')
    start = a[0].string.strip()
    now = datetime.datetime.now().strftime('%Y-%m-%d')
    now1 = datetime.datetime.now().strftime('%Y-%m-%d-%H')
    if '月' in start:
        if '年' in start:
            first = start[0:4] + '-' + start[5:7] + '-' + start[8:10] + '-' + start[12:14]
        else:
            first = '2018-' + start[0:2] + '-' + start[3:5] + '-' + start[7:9]
    elif '今天' in start:
        first = now + '-' + (start[2:4])
    elif '前' in start:
        first = now1
    return first


# 获取最后一页最后一条微博时间
def end_date(current_url, p):
    a = random.randint(0, 41)
    proxies = proxy[a]
    url = current_url[0:-1] + str(p)
    print(url)
    timeout = random.choice(range(80, 180))
    while True:
        try:
            rep = requests.get(url, headers=request_headers, timeout=timeout, proxies={"http":proxies})
            rep.encoding = 'UTF-8'
            # 页面不为空
            if not page_content(rep.text):
                break
            else:
                print('获取最后一条微博时间失败-------'+url)
                #末页打不开 最后一页推前一页
                p = p-1
                url = current_url[0:-1] + str(p)
                print('获取最后一条微博时间失败--修改后-----' + url)
                # time.sleep(2)
        except Exception as e:
            print('end_date ERROR:', e)
            time.sleep(random.choice(range(5, 15)))
    target = SoupStrainer('div', {'class': 'content'})
    bs = BeautifulSoup(rep.text, "html.parser", parse_only=target)
    time_from = bs.find_all('p',{'class':'from'})

    a = time_from[-1].find_all('a')
    while True:
        try:
            end = a[0].string.strip()
            break
        except:
            print('继续获取end time')
            time.sleep(10)
    now = datetime.datetime.now().strftime('%Y-%m-%d')
    now1 = datetime.datetime.now().strftime('%Y-%m-%d-%H')
    if '月' in end:
        if '年' in end:
            end = end[0:4] + '-' + end[5:7] + '-' + end[8:10] + '-' + end[12:14]
        else:
            end = '2018-' + end[0:2] + '-' + end[3:5] + '-' + end[7:9]
    elif '今天' in end:
        end = now + '-' + (end[2:4])
    elif '前' in end:
        end = now1
    return end


# 获取数据的方法 参数（url）
def get_data(url):
    html = get_html(url)
    total_pages = int(get_all_page(html))
    sum = 0
    lost_get = []
    result_buffer = []
    count = []
    getdata_threads = []
    g1 = MyThread(get_data_thread, args=(url, 1, total_pages, 50))
    getdata_threads.append(g1)
    g2 = MyThread(get_data_thread, args=(url, 2, total_pages, 50))
    getdata_threads.append(g2)
    g3 = MyThread(get_data_thread, args=(url, 3, total_pages, 50))
    getdata_threads.append(g3)
    g4 = MyThread(get_data_thread, args=(url, 4, total_pages, 50))
    getdata_threads.append(g4)
    g5 = MyThread(get_data_thread, args=(url, 5, total_pages, 50))
    getdata_threads.append(g5)
    g6 = MyThread(get_data_thread, args=(url, 6, total_pages, 50))
    getdata_threads.append(g6)
    g7 = MyThread(get_data_thread, args=(url, 7, total_pages, 50))
    getdata_threads.append(g7)
    g8 = MyThread(get_data_thread, args=(url, 8, total_pages, 50))
    getdata_threads.append(g8)
    g9 = MyThread(get_data_thread, args=(url, 9, total_pages, 50))
    getdata_threads.append(g9)
    g10 = MyThread(get_data_thread, args=(url, 10, total_pages, 50))
    getdata_threads.append(g10)

    g11 = MyThread(get_data_thread, args=(url, 11, total_pages, 50))
    getdata_threads.append(g11)
    g12 = MyThread(get_data_thread, args=(url, 12, total_pages, 50))
    getdata_threads.append(g12)
    g13 = MyThread(get_data_thread, args=(url, 13, total_pages, 50))
    getdata_threads.append(g13)
    g14 = MyThread(get_data_thread, args=(url, 14, total_pages, 50))
    getdata_threads.append(g14)
    g15 = MyThread(get_data_thread, args=(url, 15, total_pages, 50))
    getdata_threads.append(g15)
    g16 = MyThread(get_data_thread, args=(url, 16, total_pages, 50))
    getdata_threads.append(g16)
    g17 = MyThread(get_data_thread, args=(url, 17, total_pages, 50))
    getdata_threads.append(g17)
    g18 = MyThread(get_data_thread, args=(url, 18, total_pages, 50))
    getdata_threads.append(g18)
    g19 = MyThread(get_data_thread, args=(url, 19, total_pages, 50))
    getdata_threads.append(g19)
    g20 = MyThread(get_data_thread, args=(url, 20, total_pages, 50))
    getdata_threads.append(g20)

    g21 = MyThread(get_data_thread, args=(url, 21, total_pages, 50))
    getdata_threads.append(g21)
    g22 = MyThread(get_data_thread, args=(url, 22, total_pages, 50))
    getdata_threads.append(g22)
    g23 = MyThread(get_data_thread, args=(url, 23, total_pages, 50))
    getdata_threads.append(g23)
    g24 = MyThread(get_data_thread, args=(url, 24, total_pages, 50))
    getdata_threads.append(g24)
    g25 = MyThread(get_data_thread, args=(url, 25, total_pages, 50))
    getdata_threads.append(g25)
    g26 = MyThread(get_data_thread, args=(url, 26, total_pages, 50))
    getdata_threads.append(g26)
    g27 = MyThread(get_data_thread, args=(url, 27, total_pages, 50))
    getdata_threads.append(g27)
    g28 = MyThread(get_data_thread, args=(url, 28, total_pages, 50))
    getdata_threads.append(g28)
    g29 = MyThread(get_data_thread, args=(url, 29, total_pages, 50))
    getdata_threads.append(g29)
    g30 = MyThread(get_data_thread, args=(url, 30, total_pages, 50))
    getdata_threads.append(g30)

    g31 = MyThread(get_data_thread, args=(url, 31, total_pages, 50))
    getdata_threads.append(g31)
    g32 = MyThread(get_data_thread, args=(url, 32, total_pages, 50))
    getdata_threads.append(g32)
    g33 = MyThread(get_data_thread, args=(url, 33, total_pages, 50))
    getdata_threads.append(g33)
    g34 = MyThread(get_data_thread, args=(url, 34, total_pages, 50))
    getdata_threads.append(g34)
    g35 = MyThread(get_data_thread, args=(url, 35, total_pages, 50))
    getdata_threads.append(g35)
    g36 = MyThread(get_data_thread, args=(url, 36, total_pages, 50))
    getdata_threads.append(g36)
    g37 = MyThread(get_data_thread, args=(url, 37, total_pages, 50))
    getdata_threads.append(g37)
    g38 = MyThread(get_data_thread, args=(url, 38, total_pages, 50))
    getdata_threads.append(g38)
    g39 = MyThread(get_data_thread, args=(url, 39, total_pages, 50))
    getdata_threads.append(g39)
    g40 = MyThread(get_data_thread, args=(url, 40, total_pages, 50))
    getdata_threads.append(g40)

    g41 = MyThread(get_data_thread, args=(url, 41, total_pages, 50))
    getdata_threads.append(g41)
    g42 = MyThread(get_data_thread, args=(url, 42, total_pages, 50))
    getdata_threads.append(g42)
    g43 = MyThread(get_data_thread, args=(url, 43, total_pages, 50))
    getdata_threads.append(g43)
    g44 = MyThread(get_data_thread, args=(url, 44, total_pages, 50))
    getdata_threads.append(g44)
    g45 = MyThread(get_data_thread, args=(url, 45, total_pages, 50))
    getdata_threads.append(g45)
    g46 = MyThread(get_data_thread, args=(url, 46, total_pages, 50))
    getdata_threads.append(g46)
    g47 = MyThread(get_data_thread, args=(url, 47, total_pages, 50))
    getdata_threads.append(g47)
    g48 = MyThread(get_data_thread, args=(url, 48, total_pages, 50))
    getdata_threads.append(g48)
    g49 = MyThread(get_data_thread, args=(url, 49, total_pages, 50))
    getdata_threads.append(g49)
    g50 = MyThread(get_data_thread, args=(url, 50, total_pages, 50))
    getdata_threads.append(g50)

    for g in getdata_threads:
        g.setDaemon(True)
        g.start()
    #抓取线程结束后 程序结束
    for g in getdata_threads:
        g.join()
    for g in getdata_threads:
        sum =sum + g.get_result()[0]
        result_buffer =result_buffer+ g.get_result()[1]
        lost_get =lost_get+ g.get_result()[2]

    count.append(sum)
    count.append(result_buffer)
    count.append(lost_get)
    return count


# 分50条线程获取数据
def get_data_thread(url,start_page,end_page,d):
    sum =0
    lost_get = []
    result_buffer = []
    result_count = []
    while start_page <= end_page:
        weibo_urls = url[0:-1] + str(start_page)
        print(weibo_urls)
        html = get_html(weibo_urls)
        # 页面有没有内容
        flag_content = page_content(html)
        if not flag_content:
            try:
                result = lookup_data(html)
                sum = sum + len(result)
                print('当前页抓取条数' + str(len(result)))
                result_buffer.append(result)
                if len(result) == 0:
                    lost_get.append(weibo_urls)
            except Exception as error:
                print(error)
                continue
        elif end_page > 1 and flag_content:
            lost_get.append(weibo_urls)
        start_page = start_page + d
    result_count.append(sum)
    result_count.append(result_buffer)
    result_count.append(lost_get)
    return result_count

# 获取重刷页面数据的方法
def get_reset_data(lost_get,total):
    reset = 1  # 重刷获取失败的连接
    lost_get1 = []
    count = []
    result_buffer = []
    print(len(lost_get))
    if (len(lost_get) > 0):
        for i in range(len(lost_get)):
            print('需要重连连接' + lost_get[i])
    #重刷
    while True:
        print('第' + str(reset) + '次重刷')
        for i in range(len(lost_get)):
            weibo_urls = lost_get[i]
            print(weibo_urls)
            # 页面有没有内容
            html = get_html(weibo_urls)
            flag_content = page_content(html)
            if not flag_content:
                try:
                    result = lookup_data(html)
                    result_buffer.append(result)
                    total = total + len(result)
                    print('当前页抓取条数' + str(len(result)))
                    if len(result) == 0:
                        lost_get1.append(weibo_urls)
                except Exception as error:
                    print(error)
                    continue
            elif flag_content:
                lost_get1.append(weibo_urls)
        lost_get = lost_get1
        lost_get1 = []
        reset = reset + 1
        print('----------')
        if reset > 3:
            break

    print(len(lost_get))
    if (len(lost_get) > 0):
        for i in range(len(lost_get)):
            print('重刷后仍然失败' + lost_get[i])

    count.append(total)
    count.append(result_buffer)
    return count


# 写入csv
def make_csv(result_buffer,keyword):
    now_time = datetime.datetime.now()
    now = now_time.strftime('%Y-%m-%d %H-%M-%S.%f')
    csv_name = keyword+'.csv'
    #创建keyword 文件夹
    for i in range(0,len(result_buffer)):
        save_data(result_buffer[i], file_path+'/' + now + csv_name)

    result_buffer.clear()
    # shutil.copy(file_path+'/' + now + csv_name,upload_file_path+'/' + now + csv_name)

#获取以最后一条微博时间为筛选条件的url
def get_last_data_url(last_data):
    dateend = datetime.datetime.strptime(last_data, '%Y-%m-%d-%H')
    dateend = dateend + datetime.timedelta(hours=1)
    dateend = dateend.strftime('%Y-%m-%d-%H')
    weibo_urls = url['page_by_lastdata'] %{'dateend':dateend}
    return weibo_urls

#获取文件夹中新文件的方法
# def new_file(upload_file_path):
#     try:
#         lists = os.listdir(upload_file_path)                                    #列出目录的下所有文件和文件夹保存到lists
#         if len(lists)>0:
#             lists.sort(key=lambda fn:os.path.getmtime(upload_file_path + "\\" + fn))#按时间排序
#             file_new = os.path.join(upload_file_path,lists[-1])                     #获取最新的文件保存到file_new 全路径
#             return file_new
#     except:
#         print('文件夹还没创建')

#方法主体
def my_function(keyword,start_data,end_data):
    total = 0  # 超过多少条 存入csv
    total_count = 0  # 统计获取总数
    flag_first_fiftypage = True  # 第一次拿50条
    flag_to_diffday = True   # 在不同天内遇到同一天 跳去按时间段爬
    flag_after_hour = False  # 爬完时间段 跳回下一天
    flag_gethtml = False #第一次进入不用重新获取url
    lost_get = []
    result_buffer = []
    flag_homepage = 0 #预防首页刷不出
    flag_data = False #日期推前超过起始日期
    while True:
        weibo_url = url['home_page'] % {'keyword': keyword,'start_data':start_data,'end_data':end_data}
        #重刷三次 防止漏掉
        while flag_homepage<3:
            html = get_html(weibo_url)
            if not page_content(html):
                break
            else:
                flag_homepage = flag_homepage+1
                time.sleep(2)
        #连续刷三次 还是空 视为无数据
        if flag_homepage==3:
            print(start_data+'---'+end_data+'该日期区间无数据')
            break

        all_page = int(get_all_page(html))
        print('首页总页数' + str(all_page)+'--------'+weibo_url)

        # 总页数没有50页
        if all_page < 49:
            count = get_data(weibo_url)
            total = total + count[0]
            total_count = total_count + count[0]
            result_buffer = result_buffer + count[1]
            lost_get = lost_get + count[2]
            count.clear()
            if total > 1000:
                print('写入数据'+str(total)+start_data+'-----'+end_data)
                make_csv(result_buffer,keyword)
                total = 0
            break

        # 总页数有50页
        if all_page >=49:
            while True:
                # bugbugbug
                while flag_gethtml:
                    html = get_html(weibo_url)
                    if not page_content(html):
                        break
                    else:
                        print('获取第一页为空--------'+weibo_url)
                        # time.sleep(2)
                        if 'end_data' in weibo_url:
                        #第一页获取不了 end data向前推一天
                            data_temp = datetime.datetime.strptime(end_data, '%Y-%m-%d-%H')
                            data_temp = data_temp - datetime.timedelta(days=1)
                            data_start = datetime.datetime.strptime(start_data, '%Y-%m-%d-%H')
                            #日期推前到开始日期
                            if data_start > data_temp:
                               flag_data = True
                               break
                            end_data = data_temp.strftime('%Y-%m-%d-%H')
                            weibo_url = url['home_page'] % {'keyword': keyword, 'start_data': start_data,
                                                            'end_data': end_data}
                        #获取完小时后的url 第一页获取不了
                        else:
                            data_temp = datetime.datetime.strptime(start_time, '%Y-%m-%d')
                            data_temp = data_temp - datetime.timedelta(days=1)
                            data_start = datetime.datetime.strptime(start_data, '%Y-%m-%d-%H')
                            # 日期推前到开始日期
                            if data_start > data_temp:
                                flag_data = True
                                break
                            start_time = data_temp.strftime('%Y-%m-%d')
                            weibo_url = url['page_after_hour'] % {'keyword': keyword, 'start_data': start_data,
                                                                  'start_time': start_time}
                        print('第一页获取不了 end data向前推一天' + weibo_url)
                        flag_first_fiftypage  = True

                # 日期推前已超过开始日期 结束
                if flag_data:
                    print('日期推前已超过开始日期 结束')
                    break
                flag_gethtml = True
                all_page = int(get_all_page(html))
                first_data = start_date(html)
                start_time = first_data[0:10]
                start_hour = first_data[11:13]
                last_data = end_date(weibo_url, all_page)
                end_time = last_data[0:10]
                print(start_time + '-------------' + end_time)
                # 第一条时间 与 最后一条时间 不在同一天 不用进入小时
                if start_time != end_time:
                    flag_to_diffday = True
                    # 获取首次搜索的50页数据
                    if flag_first_fiftypage:
                        count = get_data(weibo_url)
                        total = total + count[0]
                        total_count = total_count + count[0]
                        result_buffer = result_buffer + count[1]
                        lost_get = lost_get + count[2]
                        count.clear()
                        if total > csv_limit:
                            print('写入数据'+str(total)+'-----'+ start_time + '-----' + end_time)
                            make_csv(result_buffer, keyword)
                            total = 0

                        flag_first_fiftypage = False

                    # 按小时获取完后 不在同一天的第一次获取
                    if flag_after_hour:
                        count = get_data(weibo_url)
                        total = total + count[0]
                        total_count = total_count + count[0]
                        result_buffer = result_buffer + count[1]
                        lost_get = lost_get + count[2]
                        count.clear()
                        if total > csv_limit:
                            print('写入数据'+str(total)+'-----'+ start_time + '-----' + end_time)
                            make_csv(result_buffer, keyword)
                            total = 0

                        flag_after_hour = False

                    # 获取最后一条微博时间 改下一个url
                    dateend = datetime.datetime.strptime(last_data, '%Y-%m-%d-%H')
                    dateend = dateend + datetime.timedelta(hours=1)
                    dateend = dateend.strftime('%Y-%m-%d-%H')
                    weibo_urls = url['page_by_lastdata'] % {'keyword': keyword,'start_data':start_data,'dateend': dateend}

                    while True:
                        html = get_html(weibo_urls)
                        if not page_content(html):
                            break
                        else:
                            print('获取最后一条时间为筛选的50页的首页为空--------' + weibo_urls)
                            # 第一页获取不了 end data向前推一天
                            data_temp = datetime.datetime.strptime(dateend, '%Y-%m-%d-%H')
                            data_temp = data_temp - datetime.timedelta(days=1)
                            dateend = data_temp.strftime('%Y-%m-%d-%H')
                            weibo_urls = url['page_by_lastdata'] % {'keyword': keyword, 'start_data': start_data,
                                                                    'dateend': dateend}
                            print('获取最后一条时间为筛选的50页的首页为空-----修改后---'+weibo_urls)
                            # time.sleep(2)

                    all_page = int(get_all_page(html))
                    weibo_url = weibo_urls
                    print('下一个url----' + weibo_url)
                    first_data = start_date(html)
                    start_time = first_data[0:10]
                    start_hour = first_data[11:13]
                    last_data = end_date(weibo_url, all_page)
                    end_time = last_data[0:10]
                    print(start_time + '-------------' + end_time)
                    # 如果遇到第一条与最后一条时间相同 跳去按时间段获取
                    if start_time == end_time and all_page>=49:
                        flag_to_diffday = False
                    # 获取数据 该50页第一条与最后一条时间不一样
                    if flag_to_diffday:
                        count = get_data(weibo_url)
                        total = total + count[0]
                        total_count = total_count + count[0]
                        result_buffer = result_buffer + count[1]
                        lost_get = lost_get + count[2]
                        count.clear()
                        if total > csv_limit:
                            print('写入数据'+str(total)+'-----'+ start_time + '-----' + end_time)
                            make_csv(result_buffer, keyword)
                            total = 0

                    # 如果页数少于50 结束
                    if all_page < 48:
                        print(str(all_page)+'结束')
                        break

                # 第一条时间 与 最后一条时间 在同一天 进入每小时取
                if start_time == end_time:
                    print(start_time + '-------------' + end_time)
                    for hours in range(int(start_hour), -1, -1):
                        weibo_urls = url['page_by_hour'] %{'keyword':keyword,'start_time':start_time,'hours':hours,'hours+1':hours+1}
                        html_hour = get_html(weibo_urls)
                        if page_content(html_hour):
                            print('该小时筛选为空')
                            continue
                        # 获取数据
                        count = get_data(weibo_urls)
                        total = total + count[0]
                        total_count = total_count + count[0]
                        result_buffer = result_buffer + count[1]
                        lost_get = lost_get + count[2]
                        count.clear()
                        if total > csv_limit:
                            print('写入数据'+str(total)+'-----'+ start_time + '-----' + end_time)
                            make_csv(result_buffer, keyword)
                            total = 0

                    # 按小时获取完这一天 url改成这一天之前的
                    weibo_url = url['page_after_hour'] %{'keyword':keyword,'start_data':start_data,'start_time':start_time}
                    print(weibo_url)
                    flag_first_fiftypage = False
                    flag_after_hour = True

            break

    # 重刷页面
    if len(lost_get)>0:
        count = get_reset_data(lost_get, total_count)
        total_count = count[0]
        result_buffer = result_buffer+count[1]
    if len(result_buffer)>0:
    # 剩下数据写入csv
        print('写入重刷数据'+str(total)+'-----'+ start_data + '-----' + end_data)
        make_csv(result_buffer, keyword)
    print(keyword+'抓取条数' + str(total_count)+'---'+start_data+'---'+end_data)
    return total_count

#上传csv方法
def upload_csv():
    while True:
        lists = os.listdir(upload_file_path)
        if len(lists)>0:
            #FTP传送
            # host = '10.13.0.80'
            # username = 'csv_uploader'
            # password = '123456'
            # ftp = ftplib.FTP(host)  # 实例化FTP对象
            # ftp.login(username, password)  # 登录
            # ftp.encoding = 'utf-8'
            # ftp.cwd('test')
            # file_remote = latest_file.split('\\')[-1] #上传到服务器的文件名
            # file_local = latest_file #文件的本地路径
            # bufsize = 1024  # 设置缓冲器大小
            # fp = open(file_local, 'rb')
            # ftp.storbinary('STOR ' + file_remote, fp, bufsize)
            # ftp.quit()
            for i in range(len(lists)):
                client.upload('/carson/test_upload', upload_file_path+'\\'+lists[i])
                os.remove(upload_file_path+'\\'+lists[i])
        if flag_end_upload:
            print('上传结束')
            break

threads = []
#2018-2019
t1 = MyThread(my_function,args=('伊卡璐','2009-08-16-0','2011-01-01-0',))
threads.append(t1)
# t2 = MyThread(my_function,args=('伊卡璐','2013-01-01-0','2016-01-01-0',))
# threads.append(t2)
# t3 = MyThread(my_function,args=('伊卡璐','2009-08-16-0','2013-01-01-0',))
# threads.append(t3)
# # 2017-2018
# t4 = MyThread(my_function,args=('伊卡璐','2017-09-01-0','2018-01-01-0',))
# threads.append(t4)
# t5 = MyThread(my_function,args=('伊卡璐','2017-05-01-0','2017-09-01-0',))
# threads.append(t5)
# t6 = MyThread(my_function,args=('伊卡璐','2017-01-01-0','2017-05-01-0',))
# threads.append(t6)
# #2016-2017
# t7 = MyThread(my_function,args=('伊卡璐','2016-09-01-0','2017-01-01-0',))
# threads.append(t7)
# t8 = MyThread(my_function,args=('伊卡璐','2016-05-01-0','2016-09-01-0',))
# threads.append(t8)
# t9 = MyThread(my_function,args=('伊卡璐','2016-01-01-0','2016-05-01-0',))
# threads.append(t9)
# #2015-2016
# t10 = MyThread(my_function,args=('伊卡璐','2015-09-01-0','2016-01-01-0',))
# threads.append(t10)
# t11 = MyThread(my_function,args=('伊卡璐','2015-05-01-0','2015-09-01-0',))
# threads.append(t11)
# t12 = MyThread(my_function,args=('伊卡璐','2015-01-01-0','2015-05-01-0',))
# threads.append(t12)
# #2014-2015
# t13 = MyThread(my_function,args=('伊卡璐','2014-09-01-0','2015-01-01-0',))
# threads.append(t13)
# t14 = MyThread(my_function,args=('伊卡璐','2014-05-01-0','2014-09-01-0',))
# threads.append(t14)
# t15 = MyThread(my_function,args=('伊卡璐','2014-01-01-0','2014-05-01-0',))
# threads.append(t15)
#2013-2014
# t16 = MyThread(my_function,args=('伊卡璐','2013-09-01-0','2014-01-01-0'))
# threads.append(t16)
# t17 = MyThread(my_function,args=('伊卡璐','2013-05-01-0','2014-09-01-0',))
# threads.append(t17)
# t18 = MyThread(my_function,args=('伊卡璐','2013-01-01-0','2013-05-01-0',))
# threads.append(t18)
# #2012-2013
# t19 = MyThread(my_function,args=('伊卡璐','2012-09-01-0','2013-01-01-0',))
# threads.append(t19)
# t20 = MyThread(my_function,args=('伊卡璐','2012-05-01-0','2012-09-01-0',))
# threads.append(t20)
# t21 = MyThread(my_function,args=('伊卡璐','2012-01-01-0','2012-05-01-0',))
# threads.append(t21)
# #2011-2012
# t22 = MyThread(my_function,args=('伊卡璐','2011-09-01-0','2012-01-01-0',))
# threads.append(t22)
# t23 = MyThread(my_function,args=('伊卡璐','2011-05-01-0','2011-09-01-0',))
# threads.append(t23)
# t24 = MyThread(my_function,args=('伊卡璐','2011-01-01-0','2011-05-01-0',))
# threads.append(t24)
# #2010-2011
# t25 = MyThread(my_function,args=('伊卡璐','2010-09-01-0','2011-01-01-0',))
# threads.append(t25)
# t26 = MyThread(my_function,args=('伊卡璐','2010-05-01-0','2010-09-01-0',))
# threads.append(t26)
# t27 = MyThread(my_function,args=('伊卡璐','2010-01-01-0','2010-05-01-0',))
# threads.append(t27)
# # 2009-2010
# t28 = MyThread(my_function,args=('伊卡璐','2009-08-16-0','2010-01-01-0',))
# threads.append(t28)

upload_threads = []
u1 = MyThread(upload_csv)
upload_threads.append(u1)


if __name__ == '__main__':
    start = datetime.datetime.now()
    print("时间 :", start)
    #创建一个抓取 一个上传线程
    t_count = 0
    for t in threads:
        t.setDaemon(True)
        t.start()

    flag_end_upload = False
    # u1.setDaemon(True)
    # u1.start()

    #抓取线程结束后 程序结束
    for t in threads:
        t.join()
    print('爬取线程已结束')
    # flag_a = True
    # u1.join()
    for t in threads:
        t_count = t_count + t.get_result()
    print('总统计数'+str(t_count))
    end = datetime.datetime.now()
    print("结束时间 :", end)
    print(end - start)



