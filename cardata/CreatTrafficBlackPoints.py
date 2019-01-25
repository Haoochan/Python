import csv
from math import *
import random

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

#写入生成的gps
def write_csv(result,filename):
    with open(filename, 'a', errors='ignore',newline='') as f:
        f_csv = csv.writer(f)
        for i in range(len(result)):
            f_csv.writerow((result[i]))

if __name__ == '__main__':
    traffic_black_points = []
    id=1
    for j in range(20):
        filename = 'roadGPS/road_'+str(j+1)+'.csv'
        road = 'road-'+str(j+1)
        road_gps = get_csv(filename)
        for i in range(random.randint(1,3)):
            flag = random.randint(1000, len(road_gps))
            for flag in range(flag,flag+150):
                traffic_black_points.append([id]+road_gps[flag]+[road])
            id = id +1
    write_csv(traffic_black_points,'roadGPS/traffic_black_points.csv')