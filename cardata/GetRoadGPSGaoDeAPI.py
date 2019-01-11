from math import *
import csv
import requests

# 定义一些常量
x_PI = 3.14159265358979324 * 3000.0 / 180.0
PI = 3.1415926535897932384626
a = 6378245.0
ee = 0.00669342162296594323

# 判断是否在国内，不在国内则不做偏移
def out_of_china(lng, lat):
    return (lng < 72.004 or lng > 137.8347) or (lat < 0.8293 or lat > 55.8271)

# GCJ02 转换为 WGS84
def gcj02towgs84(lng, lat):
    if out_of_china(lng, lat):
        return [lng, lat]
    else:
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
        return [round(lng * 2 - mglng,6), round(lat * 2 - mglat,6)]

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

#根据两点之间距离生成经纬度 stepTime是两点之间相隔距离 startTime=0 endTime=两个点之间总距离
def createGPSAtTwoGPS(startTime, endTime, startLng, startLat, endLng, endLat, stepTime):
    rs = []
    whileCount = (endTime - startTime) / stepTime
    for i in range(int(whileCount)):
        i=i+1
        dealTime = (endTime - (startTime + (i * stepTime))) / ((startTime + (i * stepTime)) - startTime)
        lat = ((( dealTime * startLat ) + endLat ) / ( 1 + dealTime))
        lng = ((( dealTime * startLng ) + endLng ) / ( 1 + dealTime))
        rs.append(round(lng,6))
        rs.append(round(lat,6))
    return rs

#根据两个经纬度计算距离
def geodistance(lng1,lat1,lng2,lat2): #经度1 纬度1 经度2 纬度2

    lng1, lat1, lng2, lat2 = map(radians, [float(lng1), float(lat1), float(lng2), float(lat2)])
    dlon=lng2-lng1
    dlat=lat2-lat1
    a=sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    dis = 2 * asin(sqrt(a)) * 6371 * 1000
    return dis

#读取起点终点的csv
def get_csv():
    csv_file = csv.reader(open('roadGPS/road_origin&destination.csv', 'r'))
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

#调用高德API 获取原始道路经纬度点
def get_road_info(origin,destination):
    url = 'http://restapi.amap.com/v3/direction/driving?'
    postData={
        'key':'0976905d5a7993c6833f1411a792dcb6',
        'origin':origin,
        'destination':destination,
        'extensions':'base',
        'strategy':'0',#默认 速度优先，不考虑当时路况，返回耗时最短的路线，但是此路线不一定距离最短
    }
    req = requests.get(url,postData)
    road_info = req.json()
    route = road_info['route']
    paths = route['paths']
    steps = paths[0]['steps']
    road_result = []
    #遍历所有经纬度串
    for i in range(len(steps)):
        polyline = steps[i]['polyline']
        gps = polyline.split(';')
        for j in range(len(gps)):
            if gps[j] not in road_result:
                road_result.append(gps[j])
    #gcj02坐标转wgs84坐标
    for i in range(len(road_result)):
        road_result[i] = gcj02towgs84(float(road_result[i].split(',')[0]), float(road_result[i].split(',')[1]))
    return road_result

# 根据csv文件输入的起点和终点 坐标即可生成每段路的gps坐标集
if __name__ == '__main__':
    road_origin_destination = get_csv()
    for j in range(len(road_origin_destination)):
        origin = road_origin_destination[j][1]
        destination = road_origin_destination[j][3]
        filename ='roadGPS/road_'+str(j)+'.csv'
        print(origin,destination,filename)
        road_result = get_road_info(origin,destination)
        road_gps_result = []
        total_dis =0
        #计算原始两点距离
        for i in range(len(road_result)-1):
            dis = geodistance(road_result[i][0],road_result[i][1],road_result[i+1][0],road_result[i+1][1])
            total_dis = total_dis + dis
        print(total_dis)
        createGPS = []
        #两点之间等距离生成经纬度坐标 平均距离间隔0.2m
        for i in range(len(road_result)-1):
            dis = geodistance(road_result[i][0], road_result[i][1], road_result[i + 1][0], road_result[i + 1][1])
            createGPS.append(createGPSAtTwoGPS(0,round(dis,0),float(road_result[i][0]), float(road_result[i][1]), float(road_result[i + 1][0]), float(road_result[i + 1][1]),0.2))

        dis_result = []
        #计算生成后两点距离
        for i in range(len(createGPS)):
            for j in range(0,len(createGPS[i])-4,2):
                dis = geodistance(createGPS[i][j],createGPS[i][j+1],createGPS[i][j+2],createGPS[i][j+3])
                dis_result.append(dis)

        #生成后的经纬度放到一个result
        for i in range(len(createGPS)):
            for j in range(0,len(createGPS[i])-2,2):
                temp = []
                temp.append(createGPS[i][j])
                temp.append(createGPS[i][j+1])
                road_gps_result.append(temp)

        #写入road.csv
        write_csv(road_gps_result,filename)