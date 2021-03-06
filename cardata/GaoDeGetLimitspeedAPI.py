import requests
import json
from bs4 import BeautifulSoup
import csv
from math import *
import time

# 定义一些常量
x_PI = 3.14159265358979324 * 3000.0 / 180.0
PI = 3.1415926535897932384626
a = 6378245.0
ee = 0.00669342162296594323

#计算距离
def geodistance(lng1,lat1,lng2,lat2): #经度1 纬度1 经度2 纬度2
    lng1, lat1, lng2, lat2 = map(radians, [float(lng1), float(lat1), float(lng2), float(lat2)])
    dlon=lng2-lng1
    dlat=lat2-lat1
    a=sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    dis = 2 * asin(sqrt(a)) * 6371 * 1000
    return dis

#转换纬度
def transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * sqrt(abs(lng))
    ret += (20.0 * sin(6.0 * lng * PI) + 20.0 * sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * sin(lat * PI) + 40.0 * sin(lat / 3.0 * PI)) * 2.0 / 3.0
    ret += (160.0 * sin(lat / 12.0 * PI) + 320 * sin(lat * PI / 30.0)) * 2.0 / 3.0
    return ret

#转换经度
def transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * sqrt(abs(lng))
    ret += (20.0 * sin(6.0 * lng * PI) + 20.0 * sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * sin(lng * PI) + 40.0 * sin(lng / 3.0 * PI)) * 2.0 / 3.0
    ret += (150.0 * sin(lng / 12.0 * PI) + 300.0 * sin(lng / 30.0 * PI)) * 2.0 / 3.0
    return ret

# 判断是否在国内，不在国内则不做偏移
def out_of_china(lng, lat):
    return (lng < 72.004 or lng > 137.8347) or (lat < 0.8293 or lat > 55.8271)

#wgs84转gcj02
def wgs84togcj02(lng, lat):
    """
    WGS84转GCJ02(火星坐标系)
    :param lng:WGS84坐标系的经度
    :param lat:WGS84坐标系的纬度
    :return:
    """
    if out_of_china(lng, lat):  # 判断是否在国内
        return lng, lat
    dlat = transformlat(lng - 105.0, lat - 35.0)
    dlng = transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * PI
    magic = sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * PI)
    dlng = (dlng * 180.0) / (a / sqrtmagic * cos(radlat) * PI)
    mglat = lat + dlat
    mglng = lng + dlng
    return [round(mglng,6), round(mglat,6)]

#计算经纬度之间角度 限速接口需要gps角度
def getDegree(lonA, latA, lonB, latB):
    radLatA = radians(latA)
    radLonA = radians(lonA)
    radLatB = radians(latB)
    radLonB = radians(lonB)
    dLon = radLonB - radLonA
    y = sin(dLon) * cos(radLatB)
    x = cos(radLatA) * sin(radLatB) - sin(radLatA) * cos(radLatB) * cos(dLon)
    brng = degrees(atan2(y, x))
    brng = (brng + 360) % 360
    return brng

#读取道路gps的csv
def get_csv(filename):
    csv_file=csv.reader(open(filename,'r'))
    GPS = []
    for i in csv_file:
        GPS.append(i)
    return GPS

#写入生成的gps
def write_csv(result,filename):
    with open(filename, 'a', errors='ignore',newline='') as f:
        f_csv = csv.writer(f)
        for i in range(len(result)):
            f_csv.writerow((result[i]))

#调用API获取道路限速 因为文件生成的wgs84国际坐标 调用前要转为gcj02国内坐标
#高德官网文档https://lbs.amap.com/fn/autograsp/
def get_limit_speed(lon1,lat1,lon2,lat2,lon3,lat3,lon4,lat4,limit_speed,road_name):
    # lon1 =wgs84togcj02(float(lon1),float(lat1))[0] #转换坐标格式
    # lat1 =wgs84togcj02(float(lon1),float(lat1))[1]
    # lon2 =wgs84togcj02(float(lon2),float(lat2))[0]
    # lat2 =wgs84togcj02(float(lon2),float(lat2))[1]
    # lon3 =wgs84togcj02(float(lon3),float(lat3))[0]
    # lat3 =wgs84togcj02(float(lon3),float(lat3))[1]
    # lon4 =wgs84togcj02(float(lon4),float(lat4))[0]
    # lat4 =wgs84togcj02(float(lon4),float(lat4))[1]
    lon1 =(float(lon1),float(lat1))[0] #不用转换坐标格式
    lat1 =(float(lon1),float(lat1))[1]
    lon2 =(float(lon2),float(lat2))[0]
    lat2 =(float(lon2),float(lat2))[1]
    lon3 =(float(lon3),float(lat3))[0]
    lat3 =(float(lon3),float(lat3))[1]
    lon4 =(float(lon4),float(lat4))[0]
    lat4 =(float(lon4),float(lat4))[1]
    brng1 = getDegree(lon1,lat1,lon2,lat2) #计算角度
    brng2 = getDegree(lon2,lat2,lon3,lat3)
    brng3 = getDegree(lon3,lat3,lon4,lat4)
    postData={
        'key':'0976905d5a7993c6833f1411a792dcb6',#高德地图API的key，使用者最好换成自己的 方便查看调用量限制
        'carid':'dcb6123456', #没什么意义 可以写死
        'locations':str(lon1)+','+str(lat1)+'|'+str(lon2)+','+str(lat2)+'|'+str(lon3)+','+str(lat3)+'|'+str(lon4)+','+str(lat4), #上传坐标
        'time':'1543403665,1543403666,1543403667,1543403668',#没什么意义 可以写死
        'direction': '0,'+str(brng1)+','+str(brng2)+','+str(brng3), #上传角度来算方向
        'speed':'1,1,1,1', #没什么意义 可以写死
    }
    url = 'https://restapi.amap.com/v3/autograsp?'#请求url地址
    time.sleep(0.1) #调用并发有限制 所以休眠一下
    req = requests.get(url,postData)
    content = req.json()
    lenth = 2 #正常情况 上传四个点 会有四个限速值 获取最后一个是最准确的 预防定位有误获取失败，则向前取
    while True:
        try:
            roads = content['roads']
            #一步步解析json
            limit_speed = roads[lenth]['maxspeed']
            road_name = roads[lenth]['roadname']
            if limit_speed!='-1': #有问题的话 limit_speed的值会是-1，所以向前取
                break
            else:
                lenth = lenth-1
        except:#如果该请求获取不了限速 则默认取上一次的（一般不会有）
            limit_speed = limit_speed
            road_name =road_name
            break
    print(limit_speed)
    return int(limit_speed),road_name



if __name__ == '__main__':
    # 获取下来后还需要手动调整一下限速数据，有些值会有偏差与突变 每日高德API调用量3W
    #计算这一段的坐标点 每隔30m 调用一次API 获取一个限速值 记录下来 最后存入csv
    #目前文件名每次手动修改 如有需要可改成读取文件夹的文件去生成
    filename_getgps = 'roadGPS/road_14.csv'
    filename_limitspeed = 'roadGPS/road_14_limitspeed-3.csv'
    gps = get_csv(filename_getgps)
    total_dis = 0
    limitspeed =0
    roadname =''
    limitspeed_result = []

    for i in range(len(gps)-4):
        temp =[]
        #距离间隔30m调用一次
        # dis = geodistance(gps[i][0],gps[i][1],gps[i+1][0],gps[i+1][1])
        # total_dis = dis +total_dis
        # if total_dis>=30:  #间隔距离30m
        #     total_dis = 0
        #     API_result = get_limit_speed(gps[i][0],gps[i][1],gps[i+1][0],gps[i+1][1],gps[i+2][0],gps[i+2][1],gps[i+3][0],gps[i+3][1],limitspeed,roadname)
        #     limitspeed = API_result[0]
        #     roadname =API_result[1]
        #     if limitspeed>0:
        #         temp.append(gps[i+1][0])
        #         temp.append(gps[i+1][1])
        #         temp.append(limitspeed)
        #         temp.append(roadname)
        #         limitspeed_result.append(temp)

        #开头第一个点和每隔50个点获取一次限速
        if (i%50==0) or i==0:
            API_result = get_limit_speed(gps[i][0], gps[i][1], gps[i + 1][0], gps[i + 1][1], gps[i + 2][0],
                                         gps[i + 2][1], gps[i + 3][0], gps[i + 3][1], limitspeed, roadname)
            limitspeed = API_result[0]
            roadname = API_result[1]

        if limitspeed >= 0:
            temp.append(gps[i][0])
            temp.append(gps[i][1])
            temp.append(limitspeed)
            temp.append(roadname)
            limitspeed_result.append(temp)

    #补回最后4个点
    a = -4
    for j in range(4):
        temp = []
        temp.append(gps[a][0])
        temp.append(gps[a][1])
        temp.append(limitspeed)
        temp.append(roadname)
        limitspeed_result.append(temp)
        a = a + 1





    #写入限速
    write_csv(limitspeed_result,filename_limitspeed)


