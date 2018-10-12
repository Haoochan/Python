# coding : UTF-8
import os
import requests
import csv
import random
import time
import datetime
from bs4 import BeautifulSoup


request_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'DNT': '1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/63.0.3239.26 Safari/537.36 Core/1.63.5478.400 QQBrowser/10.1.1550.400'
}


def get_html(url):
    timeout = random.choice(range(80, 180))
    while True:
        try:
            rep = requests.get(url, headers=request_headers, timeout=timeout)
            rep.encoding = 'UTF-8'
            break

        except Exception as e:
            print('get_html ERROR:', e)
            time.sleep(random.choice(range(5, 15)))

    return rep.text


def get_data(html_text):
    final = []
    bs = BeautifulSoup(html_text, "html.parser")
    data = bs.find('div', {'id': 'carlist'})
    ul = data.find('ul')
    li = ul.find_all('li')

    for car in li:
        try:
            temp = []
            car_year = ''
            mileage = ''
            city = ''
            price = ''
            msrp = ''
            car_name = ''
            i = car.find_all('i')
            try:
                car_year = i[0].string
                mileage = i[1].string
                city = i[2].find('a').string
                price = i[3].string
                msrp = i[4].string
            except Exception as e:
                pass
            temp.append(city)
            temp.append(car_name)
            temp.append(car_year)
            temp.append(mileage)
            temp.append(price)
            temp.append(msrp)
            temp.append(today_date)
            # temp.append('淘车网')

            final.append(temp)
        except Exception as e:
            print('get_data: ', e)
            continue

    return final


def save_data(data, name):
    file_name = name
    try:
        with open(file_name, 'a', errors='ignore', newline='') as f:
            f_csv = csv.writer(f)
            f_csv.writerows(data)
    except Exception as e:
        print('save_data: ', e)


def get_allcity(home_url):
    temp = []
    timeout = random.choice(range(80, 180))
    while True:
        try:
            rep = requests.get(home_url, headers=request_headers, timeout=timeout)
            rep.encoding = 'UTF-8'
            break
        except Exception as e:
            print('get_allcity-1: ', e)

    bs = BeautifulSoup(rep.text, "html.parser")
    city_list = bs.find_all('div', {'class': 'header-city-province-text'})
    for cities in city_list:
        cities = cities.find_all('a')
        for c in cities:
            try:
                href = c['href']
                href = href[2:href.find('.')]
                temp.append(href)

            except Exception as e:
                print('get_allcity-2: ', e)
                continue

    return temp


if __name__ == '__main__':

    allCity = get_allcity('http://www.taoche.com/')

    for city_name in allCity:
        for page_num in range(1, 51):
            try:
                car_url = 'http://' + city_name + '.taoche.com/all/?page=' + str(page_num) + '#pagetag'
                print(car_url)
                html = get_html(car_url)
                today_date = datetime.date.today()
                time.sleep(1)
                result = get_data(html)
                save_data(result, os.getcwd() + '/taoche_car.csv')
            except Exception as error:
                print(error)
                continue
