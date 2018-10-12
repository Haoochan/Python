# coding : UTF-8
import os
import requests
import csv
import random
import time
import datetime
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
    # 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
    #               'Chrome/67.0.3396.62 Safari/537.36'
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/69.0.3497.100 Safari/537.36'
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
    timeout = random.choice(range(80, 180))
    while True:
        try:
            rep = requests.get(url, headers=request_headers, cookies=cookies, timeout=timeout)
            rep.encoding = 'UTF-8'
            break

        except Exception as e:
            print('get_html ERROR:', e)
            time.sleep(random.choice(range(5, 15)))

    return rep.text

#获取页面数据 上面的rep.text
def get_data(html_text):
    final = []
    bs = BeautifulSoup(html_text, "html.parser")
    #页面里面的ul标签 <ul class="carlist clearfix js-top">
    li = bs.find('ul', {'class': 'carlist clearfix js-top'}).find_all('li')


    for car in li:
        try:
            temp = []
            a = car.find('a') #找到a标签
            msrp = a.find('em').string #原价
            car_info = car.text.split('\n')
            car_name = car_info[3] #a标签中第三行
            price = car_info[8] #a标签中第八行
            three_info = car_info[5].split('|') #截取年份 里程 城市
            car_year = ''
            mileage = ''
            city = ''
            try:
                car_year = three_info[0]
                mileage = three_info[1]
                city = three_info[2]
            except Exception as e: #如果没有 则置空
                pass

            temp.append(city)
            temp.append(car_name)
            temp.append(car_year)
            temp.append(mileage)
            temp.append(price)
            temp.append(msrp)
            temp.append(today_date)
            # temp.append('瓜子网')

            final.append(temp)
        except Exception as e:
            print('get_data: ', e)
            continue

    return final

#保存数据
def save_data(data, name):
    file_name = name
    try:
        with open(file_name, 'a', errors='ignore', newline='') as f:
            f_csv = csv.writer(f)
            f_csv.writerows(data)
    except Exception as e:
        print('save_data: ', e)

#获取总页数
def get_all_pages(home_url):
    timeout = random.choice(range(80, 180))
    while True:
        try:
            rep = requests.get(home_url, headers=request_headers, cookies=cookies, timeout=timeout)
            rep.encoding = 'UTF-8'
            break

        except Exception as e:
            print('get_all_pages ERROR:', e)
            time.sleep(random.choice(range(5, 15)))

    bs = BeautifulSoup(rep.text, "html.parser")
    #原来的
    tmp_span = bs.find('div', {'class': 'pageBox'})
    all_span= tmp_span.find_all('span')

    page_index = int(all_span[len(all_span) - 2].string) #总页数所在span

    return page_index

#main主函数

if __name__ == '__main__':
    # 设置cookies
    set_cookies(os.getcwd() + '/guazi_cookie.txt')
    # requests.packages.urllib3.disable_warningall_span = data.find_alls()
    all_pages = get_all_pages('https://www.guazi.com/www/buy/')

    start = datetime.datetime.now()
    print("开始时间 :", start)

    for page_num in range(1, all_pages):
        try:

            car_url = 'https://www.guazi.com/www/buy/o' + str(page_num)
            print(car_url)
            #输出url
            html = get_html(car_url)
            today_date = datetime.date.today()
            #记录现在日期
            time.sleep(1)
            result = get_data(html)
            #获取html源代码
            save_data(result, os.getcwd() + '/guazi_car.csv')
            #输出数据
            # if page_num==250:
            #     end = datetime.datetime.now()
            #     print("抓取10000条时间 :", end)
            #     print(end-start)
            #     break
            #异常处理
        except Exception as error:
            print(error)
            continue
