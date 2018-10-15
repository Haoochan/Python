# coding : UTF-8
import os
import requests
import csv
import random
import time
import datetime
import re
from bs4 import BeautifulSoup

#伪装浏览器
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

cookies = {}

#设置cookies方法
def set_cookies(cookies_path):
    try:
        f = open(cookies_path, 'r') #打开cookies文件 权限r=只读
        #循环结果遇到 ; 后分行
        #行中 =号前面是name =号后面是value 随后删除= 然后按cookies名字赋值
        for line in f.read().split(';'):
            name, value = line.strip().split('=', 1)
            cookies[name] = value
    except Exception as e:
            print('set_cookies ERROR:', e)

#获取html源文件方法
def get_html(url):
    #超时时间
    timeout = random.choice(range(80,180))
    while True:
        try:
            rep = requests.get(url, headers=request_headers, cookies=cookies, timeout=timeout)
            rep.encoding = 'UTF-8'
            break

        except Exception as e:
            print('get_html ERROR:',e)
            time.sleep(random.choice(range(5,15)))
    return rep.text

#获取页面数据
def get_data(html_text):
    final = []
    bs = BeautifulSoup(html_text,"html.parser")
    #进入微博 判断div有mid
    #data = bs.find_all('div',{'action-type':'feed_list_item'})
    data = bs.find_all('div', mid=True)
    #print('当前页面含有mid数'+str(len(data)))
    for data_info in data:
        try:
            temp = []
            #获取PostID
            PostID = data_info['mid']
            #print(PostID)
            #获取UserID
            user_info = data_info.find('div', {'class': 'info'}).find_all('a', {'class': 'name'})
            UserID = user_info[0]['href'].split('/')[-1].split('?')[0]
            #print(UserID)

            #获取PostFrom PostTime CreateTime
            from_info = data_info.find('p', {'class': 'from'}).find_all('a')
            PostTime = from_info[0].string
            if len(from_info)>1:
                PostFrom = from_info[1].string
            else:
                PostFrom='null'
            #print(PostFrom)

            #获取ForwardCount CommentCount LikeCount
            count_info = data_info.find('div', {'class': 'card-act'}).find_all('li')
            ForwardCount = count_info[1].find('a').string[3:]
            if ForwardCount=='':
                ForwardCount='0'
            CommentCount = count_info[2].find('a').string[3:]
            if CommentCount=='':
                CommentCount='0'
            LikeCount = count_info[3].find('em').string
            if LikeCount==None:
                LikeCount='0'
            # print(ForwardCount)
            # print(CommentCount)
            # print(LikeCount)

            #获取Content
            txt_count = data_info.find_all('p', {'class': 'txt'})
            #判断是否转发的微博
            forward_count = data_info.find_all('div',{'class':'card-comment'})

            #有全文 无转发
            if len(txt_count)>1 and len(forward_count)==0:
                content = data_info.find_all('p', {'class': 'txt'})
                Content = content[1].get_text().strip()
            else:
                content = data_info.find_all('p', {'class': 'txt'})
                Content = content[0].get_text().strip()
            #print(Content)

            #获取有转发的ForwardFromUserID ForwardFromPostID
            if len(forward_count)==1 :
                forward = data_info.find('ul', {'class': 'act s-fr'}).find_all('a')
                ForwardFromUserID = forward[1]['href'].split('/')[-2].split('/')[-1]
                ForwardFromPostID = forward[2]['action-data'].split('=')[-1]
            elif len(forward_count) == 0:
                ForwardFromUserID = 'null'
                ForwardFromPostID = 'null'
            # print(ForwardFromUserID)
            # print(ForwardFromPostID)

            #获取Tags
            tag_info = data_info.find_all('p', {'class': 'txt'})
            Tags = []
            tag_a = tag_info[0].find_all('a')
            if len(tag_a)>0:
                for tag in tag_a :
                    if '/weibo?q' in tag['href']:
                        Tags.append(tag.get_text())
                if Tags ==[]:
                    Tags=None
            else:
                Tags = None
            #print(Tags)

            #获取Urls 有视频的没有urls
            # 判断是否有视频
            videos_count = data_info.find_all('div', {'class': 'media media-video-a'})
            url_info = data_info.find_all('p', {'class': 'txt'})
            urls = []
            #有全文
            if len(videos_count)==0 and len(txt_count)>1 and len(forward_count)==0:
                url_a = url_info[1].find_all('a')
                if len(url_a) > 0:
                    for url in url_a:
                        if 'http://t' in url['href']:
                            urls.append(url['href'])
                    if urls==[]:
                        urls = None
                else:
                    urls = None
            #无全文
            elif len(videos_count)==0 and len(txt_count)==1 and len(forward_count)==0:
                url_a = url_info[0].find_all('a')
                if len(url_a) > 0:
                    for url in url_a:
                        if 'http://t' in url['href']:
                            urls.append(url['href'])
                    if urls==[]:
                        urls = None
                else:
                    urls = None
            else:
                urls = None
            #print(urls)

            #获取Pics 转发的图片不算
            #判断是否有图片
            m3_count = data_info.find_all('ul',{'class':'m3'})
            if  len(forward_count)==0 and len(m3_count)==1 :
                pic = data_info.find('ul', {'class': 'm3'}).find_all('img')
                Pics = []
                for p in pic:
                    pics = p['src']
                    Pics.append(pics)
            else:
                Pics = 'null'
            #print(Pics)

            #获取Videos
            try:
                if len(videos_count)==1 and len(forward_count)==0:
                    video = videos_count[0].find('a')['action-data'].split('short_url=')[-1].split('&')[-8]
                    Videos = video.replace('%3A', ':').replace('%2F', '/')
                else:
                    Videos= 'null'
            except Exception as e: #如果没有 则置空
                pass
            #print(Videos)

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
            print('get_data: ', e)
    return final

#保存数据
def save_data(data,name):
    file_name=name
    try:
        with open(file_name,'a',errors='ignore',newline='') as f:
            f_csv = csv.writer(f)
            f_csv.writerows(data)
    except Exception as e:
        print('save_data:', e)

#跳转下一页
def get_all_page(current_url):
    timeout = random.choice(range(80, 180))
    while True:
        try:
            rep = requests.get(current_url, headers=request_headers,  cookies=cookies, timeout=timeout)
            rep.encoding = 'UTF-8'
            break
        except Exception as e:
            print('get_all_pages ERROR:', e)
            time.sleep(random.choice(range(5, 15)))
    bs = BeautifulSoup(rep.text, "html.parser")
    a = bs.find('ul',{'class':'s-scroll'}).find_all('a')
    if len(a)>0:
        last = a[-1].string[1:-1]
    else:
        last = '1'
    return last

#统计每页数据数
def data_count(curr_url):
    timeout = random.choice(range(80, 180))
    while True:
        try:
            rep = requests.get(curr_url, headers=request_headers,  cookies=cookies, timeout=timeout)
            rep.encoding = 'UTF-8'
            break
        except Exception as e:
            print('data_count ERROR:', e)
            time.sleep(random.choice(range(5, 15)))
    bs = BeautifulSoup(rep.text, "html.parser")
    # # 获取总数据数
    # count = bs.find_all('p', {'class': 'result'})
    # print(count[0].string)
    # 获取每页数据
    data = bs.find_all(mid=True)
    return len(data)

#判断当前页面有没有内容
def page_content(current_url):
    timeout = random.choice(range(80, 180))
    while True:
        try:
            rep = requests.get(current_url, headers=request_headers,  cookies=cookies, timeout=timeout)
            rep.encoding = 'UTF-8'
            break
        except Exception as e:
            print('page_content ERROR:', e)
            time.sleep(random.choice(range(5, 15)))
    bs = BeautifulSoup(rep.text, "html.parser")
    # 获取总数据数
    # try:
    #     count = bs.find_all('p', {'class': 'result'})
    #     print(count[0].string)
    # except Exception as e:
    #     pass
    if bs.find('div', {'class': 'card card-no-result s-pt20b40'}):
        print('该页为空 跳过')
        return True
    else:
        return False

#判断关于该关键词微博没有了
def topic(current_url):
    timeout = random.choice(range(80, 180))
    while True:
        try:
            rep = requests.get(current_url, headers=request_headers, cookies=cookies, timeout=timeout)
            rep.encoding = 'UTF-8'
            break
        except Exception as e:
            print('topic ERROR:', e)
            time.sleep(random.choice(range(5, 15)))
    bs = BeautifulSoup(rep.text, "html.parser")
    if bs.find('div', {'class': 'card card-no-result s-pt20b40'}):
        print('该页为空 跳过')
        return True
    else:
        return False

#获取第一条微博的时间
def start_date(current_url):
    timeout = random.choice(range(80, 180))
    while True:
        try:
            rep = requests.get(current_url, headers=request_headers, cookies=cookies, timeout=timeout)
            rep.encoding = 'UTF-8'
            break
        except Exception as e:
            print('get_all_pages ERROR:', e)
            time.sleep(random.choice(range(5, 15)))
    bs = BeautifulSoup(rep.text, "html.parser")
    start_from  = bs.find_all('p',{'class':'from'})
    a = start_from[0].find_all('a')
    start = a[0].string
    now = datetime.datetime.now().strftime('%Y-%m-%d')
    now1 = datetime.datetime.now().strftime('%Y-%m-%d-%H')
    if '月' in start:
        if '年' in start:
            first = start[0:4] + '-' + start[5:7] + '-' + start[8:10] + '-' + start[12:14]
        else:
            first = '2018-' + start[0:2] + '-' + start[3:5] + '-' + start[7:9]
    elif '今天' in start:
        first =  now + '-' + (start[2:4])
    elif '前' in start:
        first = now1
    return first


#main主函数
if __name__ == '__main__':
    # 设置cookies
    set_cookies(os.getcwd() + '/weibo_cookie.txt')
    start = datetime.datetime.now()
    print("时间 :", start)
    p = 0
    sum = 0
    mid_sum = 0
    flag =True
    empty = 0
    while flag:
        weibo_url = 'https://s.weibo.com/weibo?q=韦德最后一舞&typeall=1&suball=1&Refer=g&page=1'
        all_page = int(get_all_page(weibo_url))
        print('首页总页数'+str(all_page))
        if all_page ==50: #第一条时间
            year = int(start_date(weibo_url)[0:4])
            month = int(start_date(weibo_url)[5:7])
            day = int(start_date(weibo_url)[8:10])
            while year > 2008:
                while month > 0:
                    while day > 0:
                        print(str(year) + '-' + str(month) + '-' + str(day))
                        weibo_urls = 'https://s.weibo.com/weibo?q=韦德最后一舞&typeall=1&suball=1&' \
                                     'timescope=custom:' + str(year) + '-' + str(month) + '-' + str(day) + ':' \
                                     + str(year) + '-' + str(month) + '-' + str(day) + '&Refer=g&page=1'
                        day_all_page = int(get_all_page(weibo_urls))
                        print('按天第一页总页数'+str(day_all_page))
                        # # 判断微博终结
                        # if topic(weibo_urls):
                        #     empty = empty + 1
                        #     continue
                        # else:
                        #     empty = 0

                        if day_all_page == 50:  # 如果每天超过50页 则按时间抓取数据
                            hour = int(start_date(weibo_urls)[11:13])
                            print(str(year) + '-' + str(month) + '-' + str(day)+'-'+str(hour))
                            for hours in range(hour, 0,-1):
                                weibo_urls = 'https://s.weibo.com/weibo?q=韦德最后一舞&typeall=1&suball=1&' \
                                             'timescope=custom:' + str(year) + '-' + str(month) + '-' + str(day) +'-'+str(hours-1)+ ':' \
                                             + str(year) + '-' + str(month) + '-' + str(day) + '-'+str(hours)+ '&Refer=g&page=1'
                                hour_all_page = int(get_all_page(weibo_urls))
                                print('按小时第一页总页数' + str(hour_all_page))
                                while p < hour_all_page:
                                    p = p + 1
                                    weibo_urls = 'https://s.weibo.com/weibo?q=韦德最后一舞&typeall=1&suball=1&' \
                                                 'timescope=custom:' + str(year) + '-' + str(month) + '-' + str(
                                        day) + '-' + str(hours-1) + ':' \
                                                 + str(year) + '-' + str(month) + '-' + str(day) + '-' + str(
                                        hours) + '&Refer=g&page='+str(p)
                                    print(weibo_urls)
                                    if not page_content(weibo_urls):
                                        try:
                                            html = get_html(weibo_urls)
                                            today_date = datetime.date.today()
                                            time.sleep(1)
                                            result = get_data(html)
                                            save_data(result, os.getcwd() + '/wade_weibo.csv')
                                            sum = sum + len(result)
                                            mid_sum = mid_sum + data_count(weibo_urls)
                                            print('当前页抓取条数' + str(len(result)))
                                        except Exception as error:
                                            print(error)
                                            continue
                                p=0

                        elif day_all_page<50:
                            while p < day_all_page:
                                p = p + 1
                                weibo_urls = 'https://s.weibo.com/weibo?q=韦德最后一舞&typeall=1&suball=1&' \
                                             'timescope=custom:' + str(year) + '-' + str(month) + '-' + str(day) + ':' \
                                             + str(year) + '-' + str(month) + '-' + str(day) + '&Refer=g&page='+str(p)
                                print(weibo_urls)
                                if not page_content(weibo_urls):
                                    try:
                                        html = get_html(weibo_urls)
                                        today_date = datetime.date.today()
                                        time.sleep(1)
                                        result = get_data(html)
                                        save_data(result, os.getcwd() + '/wade_weibo.csv')
                                        sum = sum + len(result)
                                        mid_sum = mid_sum + data_count(weibo_urls)
                                        print('当前页抓取条数' + str(len(result)))
                                    except Exception as error:
                                        print(error)
                                        continue
                            p=0


                        # 按日历循环
                        day = day - 1
                        #判断连续30天没有内容 话题终结
                        # if empty==30:
                        #     break
                    month = month - 1
                    if year % 4 != 0 and month == 2:
                        day = 28
                    elif year % 4 == 0 and month == 2:
                        day = 29
                    elif month == 4 or month == 6 or month == 9 or month == 11:
                        day = 30
                    else:
                        day = 31
                year = year - 1
                month = 12
            flag=False
        else:
            while p < all_page:
                p = p + 1
                weibo_urls = 'https://s.weibo.com/weibo?q=韦德最后一舞&typeall=1&suball=1&Refer=g&page='+str(p)
                print(weibo_urls)
                if not page_content(weibo_urls):
                    try:
                        html = get_html(weibo_urls)
                        today_date = datetime.date.today()
                        time.sleep(1)
                        result = get_data(html)
                        save_data(result, os.getcwd() + '/wade_weibo.csv')
                        sum = sum + len(result)
                        mid_sum = mid_sum + data_count(weibo_urls)
                        print('当前页抓取条数' + str(len(result)))
                    except Exception as error:
                        print(error)
                        continue
            flag=False

        # while p < all_page:
        #     p=p+1
        #     # weibo_urls = 'https://s.weibo.com/weibo?q=韦德最后一舞&typeall=1&suball=1&Refer=g&page=' + str(p)
        #     # weibo_urls = 'https://s.weibo.com/weibo?q=韦德最后一舞&typeall=1&suball=1&' \
        #     #              'timescope=custom:'+t2+':'+t2+'&Refer=g&page=' + str(p)
        #     weibo_urls = 'https://s.weibo.com/weibo?q=韦德最后一舞&typeall=1&suball=1&' \
        #                 'timescope=custom:2018-10-15-0:2018-10-15-0&Refer=g&page='+str(p)
        #     print(weibo_urls)
        #     if not page_content(weibo_urls):
        #         try:
        #             html = get_html(weibo_urls)
        #             today_date = datetime.date.today()
        #             time.sleep(1)
        #             result = get_data(html)
        #             save_data(result, os.getcwd()+'/wade_weibo.csv')
        #             sum = sum + len(result)
        #             mid_sum = mid_sum + data_count(weibo_urls)
        #             print('当前页抓取条数'+str(len(result)))
        #         except Exception as error:
        #             print(error)
        #             continue

    print('-------------')
    print('抓取条数'+str(sum))
    #print('含有mid条数'+str(mid_sum))
    end = datetime.datetime.now()
    print("结束时间 :", end)
    print(end - start)

    # try:
    #     weibo_urls = 'https://s.weibo.com/weibo?q=最后一舞先生&typeall=1&suball=1&Refer=g&page=36'#%E6%BD%98%E5%A9%B7
    #     print(weibo_urls)
    #     html = get_html(weibo_urls)
    #     today_date = datetime.date.today()
    #     time.sleep(2)
    #     result = get_data(html)
    #     save_data(result, os.getcwd() + '/panting_weibo.csv')
    # except Exception as error:
    #     print(error)