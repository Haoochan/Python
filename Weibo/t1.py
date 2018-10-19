from bs4 import BeautifulSoup
import re
import datetime
import time


# now_time = datetime.datetime.now()
# now1 = now_time.strftime('%Y-%m-%d %H:%M:%S.%f')
# csv_name = 'wade_weibo.csv'
# new_name = now1+csv_name
# print(now1)
# print(new_name)
# time.sleep(1)
# now_time = datetime.datetime.now()
# now2 = now_time.strftime('%Y-%m-%d %H:%M:%S')
# print(now2)
# now3=now_time+datetime.timedelta(hours=-1)
# now4=now_time+datetime.timedelta(days=-1)
# now5=now_time+datetime.timedelta(days=-30)
# now6=now_time+datetime.timedelta(days=-365)
# print(now3.strftime('%Y-%m-%d %H:%M:%S'))
# print(now4.strftime('%Y-%m-%d %H:%M:%S'))
# print(now5.strftime('%Y-%m-%d %H:%M:%S'))
# print(now6.strftime('%Y-%m-%d'))

# now = datetime.datetime.now().strftime('%Y-%m-%d')
# now1 = datetime.datetime.now().strftime('%Y-%m-%d-%H')
# a = '10月11日 22:59'
# #a = '4秒前'
# if '月' in a :
#     if '年' in a:
#         print(a[0:4]+'-'+a[5:7]+'-'+a[8:10]+'-'+a[12:14])
#     else:
#         print('2018-'+a[0:2]+'-'+a[3:5]+'-'+a[7:9])
# elif '今天' in a:
#     print(now + '-' + (a[2:4]))
# elif '前' in a:
#     print(now1)

# now = datetime.datetime.now().strftime('%Y-%m-%d')
# now1 = datetime.datetime.now().strftime('%Y-%m-%d-%H')
# b= '今天08:59'
# if '今天' in b:
#     print(now)
#     h = int(b[2:4])+1
#     print(now+'-'+(b[2:4]))
#     print(now+'-'+str(h))
# c = '4秒前'
# if '前' in c:
#     print(now)
#     print(now1)



# first_data = '2018-08-15-23'
# start_time = first_data
# end_time = '2018-8-01'
# year = int(first_data[0:4]) #2018
# month = int(first_data[5:7]) #10
# day = int(first_data[8:10]) #16
# hour = int(first_data[11:13]) #14
#start_time1 = first_data[0:8]+str(day+1)
# datestart = datetime.datetime.strptime(start_time, '%Y-%m-%d-%H')
# datestart=datestart+datetime.timedelta(hours=1)
# #dateend = datetime.datetime.strptime(end_time, '%Y-%m-%d-%H')
# a = datestart.strftime('%Y-%m-%d-%H')
# weibo_urls = 'https://s.weibo.com/weibo?q=泰国小老板紫菜好吃的&typeall=1&suball=1&' \
#              'timescope=custom:' + ':' \
#              + a + '&Refer=g&page=1'
# print(weibo_urls)
#
# while datestart > dateend:
#     datestart -= datetime.timedelta(days=1)
#     begin_time=datestart.strftime('%Y-%m-%d')
#     begin_time_a = datestart+datetime.timedelta(days=1)
#     begin_time1 = begin_time_a.strftime('%Y-%m-%d')
#     print(begin_time)
#     print(begin_time1)
#     weibo_urls = 'https://s.weibo.com/weibo?q=小老板紫菜好吃的&typeall=1&suball=1&' \
#                  'timescope=custom:' + begin_time + ':' \
#                  + begin_time1 + '-0&Refer=g&page=1'
#     print(weibo_urls)

# last_data = '2018-10-16-14'
# hour = int(last_data[11:13])
#
# datestart = datetime.datetime.strptime(last_data, '%Y-%m-%d-%H')
# dateend = datestart + datetime.timedelta(hours=1)
# datestart = datestart.strftime('%Y-%m-%d-%H')
# dateend = dateend.strftime('%Y-%m-%d-%H')
# for i in range(hour, 24):
#     weibo_urls = 'https://s.weibo.com/weibo?q=泰国小老板紫菜&typeall=1&suball=1&' \
#                  'timescope=custom:'+datestart+':' \
#                  + dateend + '&Refer=g&page=1'
#     print(weibo_urls)

# start_time  = '2018-10-16'
# p=2
# weibo_url = 'https://s.weibo.com/weibo?q=邓超&typeall=1&suball=1&' \
#              'timescope=custom:'+':' \
#              + start_time +'-0&Refer=g&page=1'
# print(weibo_url[0:-1]+str(p))

# lost = ['1', '2', '3', '4', '5', '1', '1', '1', '1', '1',]
# lost1=[]
# flag = 1
# while True:
#     for i in range(len(lost)):
#         print('第'+str(flag)+'次重刷')
#         # weibo_urls = lost[i]
#         # print(weibo_urls)
#         # # 页面有没有内容
#         # flag3 = page_content(weibo_urls)
#         # if not flag3:
#         #     try:
#         #         html = get_html(weibo_urls)
#         #         today_date = datetime.date.today()
#         #         time.sleep(0.5)
#         #         result = get_data(html)
#         #         save_data(result, os.getcwd() + '/wade_weibo.csv')
#         #         sum = sum + len(result)
#         #         # mid_sum = mid_sum + data_count(weibo_urls)
#         #         print('当前页抓取条数' + str(len(result)))
#         #         if len(result) == 0:
#         #             lost1.append(weibo_urls)
#         #     except Exception as error:
#         #         print(error)
#         #         continue
#         # elif flag3:
#         #     lost1.append(weibo_urls)
#     lost = lost1
#     lost1 = []
#     flag = flag+1
#     print('----------')
#     if flag>3:
#         break

# a = ['d','s','da',['a','d']]
# b= [['a','d'],'gd','afa']
# a = a+b
# for i in range(len(a)):
#     print(a[i])
url = {
    'home_page':'https://s.weibo.com/weibo?q=伊卡璐洗发露&typeall=1&suball=1&Refer=g&page=1'
    'page_by_hour':'https://s.weibo.com/weibo?q=伊卡璐洗发露&typeall=1&suball=1&' \
                                     'timescope=custom:' + start_time + '-' + str(hours) + ':' \
                                     + start_time + '-' + str(hours + 1) + '&Refer=g&page=1'

}



