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
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
from fake_useragent import UserAgent

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

proxies = {"http":"http://118.190.95.35:9001"}

keyword = '伊卡璐洗发露'
csv_limit = 1000
test_file_path='E:\\GitHub\\Python\\'+keyword#目录地址
url = {
    'home_page':'https://s.weibo.com/weibo?q='+keyword+'&typeall=1&suball=1&Refer=g&page=1',
    'page_by_lastdata':'https://s.weibo.com/weibo?q='+keyword+'&typeall=1&suball=1&' \
                         'timescope=custom:' + ':' \
                         '%(dateend)s&Refer=g&page=1',
    'page_by_hour':'https://s.weibo.com/weibo?q='+keyword+'&typeall=1&suball=1&' \
                                     'timescope=custom:%(start_time)s-%(hours)d: '\
                                     '%(start_time)s-%(hours+1)d&Refer=g&page=1',
    'page_after_hour':'https://s.weibo.com/weibo?q='+keyword+'&typeall=1&suball=1&' \
                                'timescope=custom:' + ':' \
                                '%(start_time)s-0&Refer=g&page=1'
}

# 获取html源文件方法
def get_html(url):
    # 超时时间
    timeout = random.choice(range(80, 180))
    request_headers.update({'User-Agent': ua.chrome})
    while True:
        try:
            rep = requests.get(url, headers=request_headers, timeout=timeout, proxies=proxies)
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
            PostID = data_info['mid']
            # print(PostID)
            # 获取UserID
            user_info = data_info.find('div', {'class': 'info'}).find_all('a', {'class': 'name'})
            UserID = user_info[0]['href'].split('/')[-1].split('?')[0]
            # print(UserID)

            # 获取PostFrom PostTime CreateTime
            from_info = data_info.find('p', {'class': 'from'}).find_all('a')
            PostTime = from_info[0].string.strip()
            if len(from_info) > 1:
                PostFrom = from_info[1].string
            else:
                PostFrom = 'null'
            # print(PostFrom)

            # 获取ForwardCount CommentCount LikeCount
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
            # print(ForwardCount)
            # print(CommentCount)
            # print(LikeCount)

            # 获取Content
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
            # print(Content)

            # 获取有转发的ForwardFromUserID ForwardFromPostID
            if len(forward_count) == 1:
                forward = data_info.find('ul', {'class': 'act s-fr'}).find_all('a')
                ForwardFromUserID = forward[1]['href'].split('/')[-2].split('/')[-1]
                ForwardFromPostID = forward[2]['action-data'].split('=')[-1]
            else:
                ForwardFromUserID = 'null'
                ForwardFromPostID = 'null'
            # print(ForwardFromUserID)
            # print(ForwardFromPostID)

            # 获取Tags
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
            # print(Tags)

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
                        urls = None
                else:
                    urls = None
            # 无全文
            elif len(videos_count) == 0 and len(txt_count) == 1 and len(forward_count) == 0:
                url_a = url_info[0].find_all('a')
                if len(url_a) > 0:
                    for url in url_a:
                        if 'http://t' in url['href']:
                            urls.append(url['href'])
                    if urls == []:
                        urls = None
                else:
                    urls = None
            else:
                urls = None
            # print(urls)

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
            # print(Pics)

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
            # print(Videos)

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
        with open(file_name, 'a', errors='ignore', newline='',encoding='utf-8') as f:
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


# 判断当前页面
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
    url = current_url[0:-1] + str(p)
    print(url)
    timeout = random.choice(range(80, 180))
    while True:
        try:
            rep = requests.get(url, headers=request_headers, timeout=timeout, proxies=proxies)
            rep.encoding = 'UTF-8'

            # 页面不为空
            if not page_content(rep.text):
                break
            else:
                time.sleep(2)
        except Exception as e:
            print('end_date ERROR:', e)
            time.sleep(random.choice(range(5, 15)))
    target = SoupStrainer('div', {'class': 'content'})
    bs = BeautifulSoup(rep.text, "html.parser", parse_only=target)
    a = bs.find_all('a')
    end = a[-2].string.strip()
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
    p = 0
    sum = 0
    lost_get = []
    result_buffer = []
    count = []
    while p < total_pages:
        p = p + 1
        weibo_urls = url[0:-1] + str(p)
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
        elif total_pages > 1 and flag_content:
            lost_get.append(weibo_urls)


    count.append(sum)
    count.append(result_buffer)
    count.append(lost_get)
    return count


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
        time.sleep(1)
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


# 写入
def make_csv(result_buffer):
    print('写入数据')
    now_time = datetime.datetime.now()
    now = now_time.strftime('%Y-%m-%d %H-%M-%S.%f')
    csv_name = keyword+'.csv'
    #创建keyword 文件夹
    file_path = os.getcwd()[:-5] + keyword + '\\'
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    for i in range(0,len(result_buffer)):
        save_data(result_buffer[i], file_path+'/' + now + csv_name)
    result_buffer.clear()
    # shutil.copy(file_path + '/' + now + csv_name, 'E:/GitHub/Python/'+keyword+'1')


#获取以最后一条微博时间为筛选条件的url
def get_last_data_url(last_data):
    dateend = datetime.datetime.strptime(last_data, '%Y-%m-%d-%H')
    dateend = dateend + datetime.timedelta(hours=1)
    dateend = dateend.strftime('%Y-%m-%d-%H')
    # weibo_urls = 'https://s.weibo.com/weibo?q='+keyword+'&typeall=1&suball=1&' \
    #              'timescope=custom:' + ':' \
    #              + dateend + '&Refer=g&page=1'

    weibo_urls = url['page_by_lastdata'] %{'dateend':dateend}
    return weibo_urls

#获取文件夹中新文件的方法
def new_file(test_file_path):
    try:
        lists = os.listdir(test_file_path)                                    #列出目录的下所有文件和文件夹保存到lists
        print(lists)
        if len(lists)>0:
            lists.sort(key=lambda fn:os.path.getmtime(test_file_path + "\\" + fn))#按时间排序
            file_new = os.path.join(test_file_path,lists[-1])                     #获取最新的文件保存到file_new 全路径
            print(file_new)
            return file_new
        else:
            print('文件为空')
            return None
    except:
        print('文件夹还没创建')

#方法主体
def my_function():
    total = 0  # 超过多少条 存入csv
    total_count = 0  # 统计获取总数
    flag_first_fiftypage = True  # 第一次拿50条
    flag_to_diffday = True   # 在不同天内遇到同一天 跳去按时间段爬
    flag_after_hour = False  # 爬完时间段 跳回下一天
    lost_get = []
    result_buffer = []
    while True:
        # weibo_url = 'https://s.weibo.com/weibo?q=伊卡璐洗发露&typeall=1&suball=1&Refer=g&page=1'
        weibo_url = url['home_page']
        html = get_html(weibo_url)
        all_page = int(get_all_page(html))
        print('首页总页数' + str(all_page))

        # 总页数没有50页
        if all_page < 50:
            count = get_data(weibo_url)
            total = total + count[0]
            total_count = total_count + count[0]
            result_buffer = result_buffer + count[1]
            lost_get = lost_get + count[2]
            count.clear()
            if total > 1000:
                make_csv(result_buffer)
                total = 0
            break

        # 总页数有50页
        if all_page == 50:
            while True:
                while True:
                    html = get_html(weibo_url)
                    if not page_content(html):
                        break
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
                            make_csv(result_buffer)
                            total = 0

                        if all_page == 50:
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
                            make_csv(result_buffer)
                            total = 0

                        flag_after_hour = False

                    # 获取最后一条微博时间 改下一个url
                    weibo_urls = get_last_data_url(last_data)

                    while True:
                        html = get_html(weibo_urls)
                        if not page_content(html):
                            break

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
                    if start_time == end_time:
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
                            make_csv(result_buffer)
                            total = 0

                    # 如果页数少于50 结束
                    if all_page < 50:
                        break

                # 第一条时间 与 最后一条时间 在同一天 进入每小时取
                if start_time == end_time:
                    print(start_time + '-------------' + end_time)
                    for hours in range(int(start_hour), -1, -1):
                        # weibo_urls = 'https://s.weibo.com/weibo?q='+keyword+'&typeall=1&suball=1&' \
                        #              'timescope=custom:' + start_time + '-' + str(hours) + ':' \
                        #              + start_time + '-' + str(hours + 1) + '&Refer=g&page=1'
                        weibo_urls = url['page_by_hour'] %{'start_time':start_time,'hours':hours,'hours+1':hours+1}
                        # 获取数据
                        count = get_data(weibo_urls)
                        total = total + count[0]
                        total_count = total_count + count[0]
                        result_buffer = result_buffer + count[1]
                        lost_get = lost_get + count[2]
                        count.clear()
                        if total > csv_limit:
                            make_csv(result_buffer)
                            total = 0

                    # 按小时获取完这一天 url改成这一天之前的
                    # weibo_url = 'https://s.weibo.com/weibo?q='+keyword+'&typeall=1&suball=1&' \
                    #             'timescope=custom:' + ':' \
                    #             + start_time + '-0&Refer=g&page=1'
                    weibo_url = url['page_after_hour'] %{'start_time':start_time}
                    print(weibo_url)
                    flag_first_fiftypage = False
                    flag_after_hour = True

            break

    # 重刷页面
    count = get_reset_data(lost_get, total_count)
    total_count = count[0]
    result_buffer = result_buffer+count[1]
    # 剩下数据写入csv
    make_csv(result_buffer)
    time.sleep(10)
    print('-------------')
    print('抓取条数' + str(total_count))

#上传csv方法
def upload_csv(keyword):
    while True:
        time.sleep(10)
        latest_file = new_file(test_file_path)
        if latest_file!=None:
            host = '10.13.0.80'
            username = 'csv_uploader'
            password = '123456'
            ftp = ftplib.FTP(host)  # 实例化FTP对象
            ftp.login(username, password)  # 登录
            ftp.encoding = 'utf-8'
            ftp.cwd('test')
            file_remote = latest_file.split('\\')[-1] #上传到服务器的文件名
            file_local = latest_file #文件的本地路径
            bufsize = 1024  # 设置缓冲器大小
            fp = open(file_local, 'rb')
            ftp.storbinary('STOR ' + file_remote, fp, bufsize)
            ftp.dir()
            now = datetime.datetime.now()
            print(now)
            ftp.quit()


if __name__ == '__main__':
    start = datetime.datetime.now()
    print("时间 :", start)
    #创建一个抓取 一个上传线程
    threads = []
    t1 = threading.Thread(target=my_function)
    threads.append(t1)
    t2 = threading.Thread(target=upload_csv,args=(keyword,))
    threads.append(t2)
    for t in threads:
        t.setDaemon(True)
        t.start()
    #抓取线程结束后 程序结束
    t1.join()

    end = datetime.datetime.now()
    print("结束时间 :", end)
    print(end - start)



