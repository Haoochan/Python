from bs4 import BeautifulSoup
import re
import datetime
import time


# now_time = datetime.datetime.now()
# now1 = now_time.strftime('%Y-%m-%d %H:%M:%S')
# print(now1)
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

a='2018-10-15-14'
print(a[0:4])
print(a[5:7])
print(a[8:10])
year = int(a[0:4])
month = int(a[5:7])
day = int(a[8:10])
hour = int()
while year>2008:
    while month>0:
        while day>0:
                print(str(year)+'-'+str(month)+'-'+str(day))
                day=day-1
        month=month-1
        if year%4!=0 and month==2:
            day=28
        elif year%4==0 and month==2:
            day=29
        elif month==4 or month==6 or month==9 or month==11:
            day=30
        else:
            day=31
    year = year-1
    month=12
