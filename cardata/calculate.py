import csv
from math import *
import datetime
# 测试计算 平均速度 最大速度 交通黑点数 急刹车次数 急加速次数 开始时间 结束时间

#计算两点间距离
def geodistance(lng1,lat1,lng2,lat2): #经度1 纬度1 经度2 纬度2
    lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])
    dlon=lng2-lng1
    dlat=lat2-lat1
    a=sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    dis = 2 * asin(sqrt(a)) * 6371 * 1000
    return dis

#读取道路gps
def get_csv(filename):
    csv_file=csv.reader(open(filename,'r'))
    GPS = []
    for i in csv_file:
        GPS.append(i)
    return GPS

#读取交通黑点
def get_traffic_blackpoint():
    csv_file=csv.reader(open('E:\\Python\\Cardata\\roadGPS\\traffic_black_points.csv','r'))
    traffic_blackpoint = []
    for i in csv_file:
        traffic_blackpoint.append(i)
    return traffic_blackpoint

#根据tripsId 统计csv文件里面有多少段trip 分割
def split_gps(gps):
    a = int(gps[0][1])
    GPS=[]
    gps1=[]
    for i in range(len(gps)):
        if int(gps[i][1])==a:
            gps1.append(gps[i])
        if int(gps[i][1])!=a or i==len(gps)-1:
            a=int(gps[i][1])
            GPS.append(gps1)
            gps1=[]
            gps1.append(gps[i])
    return GPS

#计算时间
def get_seconds(start,end):
    start = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M:%S.%f")
    end = datetime.datetime.strptime(end, "%Y-%m-%d %H:%M:%S.%f")
    second = (end-start).total_seconds()
    return second


#计算平均速度
def calculate_average_speed(gps):
    for i in range(len(gps)): #分开两段(文件切开多少段)
        total_dis = 0
        total_second = 0
        top_speed = 0
        speed=[]
        # 计算平均速度和最高速度 遍历相邻gps 计算出每秒的速度
        for j in range(len(gps[i])-1):
            dis =geodistance(float(gps[i][j][2]),float(gps[i][j][3]),float(gps[i][j+1][2]),float(gps[i][j+1][3]))
            second =get_seconds(gps[i][j][5],gps[i][j+1][5])
            total_dis = total_dis + dis
            total_second=total_second + second
            curr_speed=dis/second
            speed.append(curr_speed)
            if curr_speed>top_speed:
                top_speed=curr_speed


        # #计算急加速 急刹车
        # 计算思路 百度地图的标准 每秒加速度变化超过1.67 且持续2秒以上视为急变速
        # 所以遍历速度的list，所以算2秒的速度差值，超过4，并且两次急变速时间间隔超过4秒 则记作一次急变速
        heavy_brake_count=0
        heavy_accelerate_count=0
        a=0
        for k in range(len(speed)-2):
            temp = speed[k + 2] - speed[k]
            if temp >= 4:
                if k - a >= 4:
                    heavy_accelerate_count = heavy_accelerate_count + 1
                    a = k
            if temp <= -4:
                if k - a >= 4:
                    heavy_brake_count = heavy_brake_count + 1
                    a = k

        #开始时间 结束时间
        start_time=gps[i][0][5]
        end_time=gps[i][-1][5]

        #计算交通黑点
        traffic_black_point_count=0
        for l in range(len(traffic_black_point)):
            for m in range(len(gps[i])):
                black_point_dis = geodistance(float(gps[i][m][2]),float(gps[i][m][3]),float(traffic_black_point[l][1]),float(traffic_black_point[l][2]))
                if black_point_dis<=20:
                    traffic_black_point_count = traffic_black_point_count + 1
                    break


        print('平均时速-----'+str(total_dis/total_second))
        print('最高速度-----' + str(top_speed))
        print('急加速次数-----' + str(heavy_accelerate_count))
        print('急减速次数-----' + str(heavy_brake_count))
        print('开始时间-----' + start_time)
        print('结束时间-----' + end_time)
        print('交通黑点-----',traffic_black_point_count)


if __name__ == '__main__':
    filename='E:\\Python\\Cardata\\upload\\position1-file-.csv'
    gps = get_csv(filename)
    gps_spilt=split_gps(gps)
    traffic_black_point = get_traffic_blackpoint()
    calculate_average_speed(gps_spilt)






