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


#获取html源文件方法
def get_html(url):
    #超时时间
    timeout = random.choice(range(80,180))
    while True:
        try:
            rep = requests.get(url,headers=request_headers,timeout=timeout)
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
    data = bs.find_all(mid=True)
    #print(data)
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
            #有bug 有些微博没有PostFrom
            from_info = data_info.find('p', {'class': 'from'}).find_all('a')
            try:
                PostTime = from_info[0].string
                PostFrom = from_info[1].string
                #print(PostFrom)
            except Exception as e: #如果没有 则置空
                pass
            #获取ForwardCount CommentCount LikeCount
            count_info = data_info.find('div', {'class': 'card-act'}).find_all('li')
            ForwardCount = count_info[1].find('a').string
            CommentCount = count_info[2].find('a').string
            LikeCount = count_info[3].find('em').string
            # print(ForwardCount)
            # print(CommentCount)
            # print(LikeCount)

            #获取Content
            txt_count = data_info.find_all('p', {'class': 'txt'})
            #判断是否转发的微博
            forward_count = data_info.find_all('div',{'class':'card-comment'})
            #有全文 无转发
            if len(txt_count)>1:
                content = data_info.find_all('p', {'class': 'txt'})
                Content = content[1].get_text().strip()
                #print(Content)
                #print('----------有全文----------------')
            else:
                content = data_info.find('p', {'class': 'txt'})
                Content = content.get_text().strip()
                #print(Content)
                #print('--------无全文--------')

            #获取有转发的ForwardFromUserID ForwardFromPostID
            if len(forward_count)==1 :
                forward = data_info.find('ul', {'class': 'act s-fr'}).find_all('a')
                ForwardFromUserID = forward[1]['href'].split('/')[-2].split('/')[-1]
                ForwardFromPostID = forward[2]['action-data'].split('=')[-1]
                #print(ForwardFromUserID)
                #print(ForwardFromPostID)
            else :
                ForwardFromUserID = 'null'
                ForwardFromPostID = 'null'
                #print(ForwardFromUserID)
                #print(ForwardFromPostID)

            #获取Tags

            #获取Urls

            #获取Pics 转发的图片不算
            if  len(forward_count)==0:
                pic = data_info.find('ul', {'class': 'm3'}).find_all('img')
                print(len(pic))
                for p in range(1,len(pic)):
                    img = p['src']
                    print(img)
            else:
                img = 'null'
                print(img)
            #获取Videos


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


            final.append(temp)

        except Exception as e:
            print('get_data: ', e)
            #continue

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


#main主函数
if __name__ == '__main__':
    try:
        weibo_url = 'https://s.weibo.com/weibo?q=%E6%BD%98%E5%A9%B7&Refer=index&page=1'
        print(weibo_url)
        html = get_html(weibo_url)
        today_date = datetime.date.today()
        time.sleep(1)
        result = get_data(html)
        save_data(result, os.getcwd()+'/panting_weibo.csv')

    except Exception as error:
        print(error)
