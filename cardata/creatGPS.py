from math import *
import csv
import random
import datetime
from hdfs.client import *

#生成日志
class Logger(object):
    def __init__(self, fileN="Default.log"):
        self.terminal = sys.stdout
        self.log = open(fileN, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass

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

# sys.stdout = Logger("C:\\Users\\Rayho.chen\\Desktop\\v3.txt")

#写入生成的gps
def write_csv(result,filename):
    with open(filename, 'a', errors='ignore',newline='') as f:
        f_csv = csv.writer(f)
        f_csv.writerow((result))

#急加速
def quick_starts(v):
    v1 = v + random.uniform(2,3.5)
    return v1

#急减速
def quick_stops(v):
    v1 = v - random.uniform(2, 3.5)
    return v1

#正常加速
def normal_starts(v):
    v1 = v + random.uniform(0.4,0.6)
    return v1

#正常减速
def normal_stops(v):
    v1 = v - random.uniform(0.4,0.6)
    return v1

#正常行驶
def normal_driving(v):
    v1 = v + random.uniform(-0.2,0.2)
    if v1<=0:
        v1=0
    return v1

#启动
def starts(v):
    v1 = v + random.uniform(0.8,1.2)
    return v1

#最后减速到停车
def stops(v):
    v1 = v - random.uniform(0.5,1)
    if v1<0:
        v1 = 0
    return v1

#时速超过120 调低一点
def change_limitspeed(limitspeed):
    if limitspeed>=33:
        limitspeed = 27
    return limitspeed


#生成gps数据
def createGPS(trip_id,pos_id,time):
    gps = get_csv(initial_gps_filename)
    total_dis = 0
    current_v = 0
    sec_quick = 0 #急变速持续时间
    sec_accelerate = 0 #普通加速持续时间
    sec_decelerate = 0 #普通减速持续时间
    sec_normal = 0 #正常行驶持续时间
    sec_starts =0 #启动持续时间
    sec_stops = 0 #trip即将结束减速时间
    sec_normal_in_stop = 0 #trip即将结束中匀速时间
    flag_quick_change = False #急加速急减速
    flag_normal_acclerate = False #正常加速
    flag_normal_stops = False #正常减速
    flag_normal_driving = False #正常匀速行驶
    flag_stop = True #停车
    flag_start = False #停车后启动
    flag_break = False #trip即将结束的减速
    flag_break_normal = False #trip即将结束中的匀速
    quick_range = 300  # 急变速概率范围
    normal_range = 50  # 普通加减速概率范围
    result = []
    v_quick_change = 0 #急加速 急减速 标签
    # 获取道路限速
    limitspeedcsv = get_csv(limitspeed_filename)
    flag_limitspeed=0
    limit_speed = int(limitspeedcsv[flag_limitspeed][2])/3.6
    limit_speed_1 = int(limitspeedcsv[flag_limitspeed][2])/3.6
    # 添加开始位置gps
    result.append(gps[0]+[current_v])
    # result.append(gps[0] + [current_v] + [limit_speed])

    for i in range(len(gps) - 1):
        #获取限速
        try:
            limitspeed_dis_first = geodistance(float(gps[i][0]), float(gps[i][1]), float(limitspeedcsv[flag_limitspeed][0]), float(limitspeedcsv[flag_limitspeed][1]))
            limitspeed_dis_second = geodistance(float(gps[i][0]), float(gps[i][1]), float(limitspeedcsv[flag_limitspeed+1][0]),
                                               float(limitspeedcsv[flag_limitspeed+1][1]))

            if limitspeed_dis_first<=limitspeed_dis_second:
                limit_speed = int(limitspeedcsv[flag_limitspeed][2]) / 3.6
                limit_speed_1 = int(limitspeedcsv[flag_limitspeed][2]) / 3.6
            #限速变为下一个限速值
            elif limitspeed_dis_first>limitspeed_dis_second:
                limit_speed = int(limitspeedcsv[flag_limitspeed+1][2]) / 3.6
                limit_speed_1 = int(limitspeedcsv[flag_limitspeed+1][2]) / 3.6
                flag_limitspeed = flag_limitspeed + 1
        except:
            limit_speed = int(limitspeedcsv[flag_limitspeed][2])/3.6
            limit_speed_1 = int(limitspeedcsv[flag_limitspeed][2]) / 3.6

        dis = geodistance(float(gps[i][0]), float(gps[i][1]), float(gps[i + 1][0]), float(gps[i + 1][1]))
        total_dis = total_dis + dis

        #结束 减速停车
        if i>= (len(gps) - 1-6000):
            if current_v>0:
                if total_dis>=current_v:
                    total_dis = 0
                    result.append(gps[i+1] + [current_v])
                    # result.append(gps[i + 1] + [current_v] + [limit_speed])
                    b = random.randint(1,2)
                    if (b==2 or flag_break) and flag_break_normal==False:
                        # print('减速')
                        flag_break = True
                        sec_stops = sec_stops + 1
                        current_v = stops(current_v)
                        if current_v < 0:
                            current_v = 0
                        if sec_stops>=random.randint(2,4):
                            sec_stops = 0
                            flag_break = False
                        continue
                    if flag_break==False or flag_break_normal or b==1:
                        sec_normal_in_stop = sec_normal_in_stop +1
                        flag_break_normal = True
                        # print('匀速')
                        current_v=normal_driving(current_v)
                        if sec_normal_in_stop>=random.randint(4,6):
                            sec_normal_in_stop = 0
                            flag_break_normal = False
                    if current_v < 0:
                        current_v=0
                continue
            else:
                for k in range(random.randint(10, 25)):
                    result.append(gps[i+1] + [0])
                    # result.append(gps[i + 1] + [0] + [limit_speed])
                break

        #停车
        if flag_stop:
            if current_v>0:
                if total_dis>=current_v:
                    total_dis = 0
                    result.append(gps[i+1] + [current_v])
                    # result.append(gps[i + 1] + [current_v] + [limit_speed])
                    current_v = normal_stops(current_v)
            if current_v<=0:
                current_v = 0
                stop_seconds = random.randint(10, 25)
                for j in range(stop_seconds):
                    result.append(gps[i] + [current_v])
                    # result.append(gps[i] + [current_v] + [limit_speed])
                flag_stop = False
                flag_start = True
                #接启动
                current_v = normal_starts(current_v)
            continue

        #启动
        if flag_start:
            if total_dis>=current_v:
                total_dis = 0
                result.append(gps[i+1] + [current_v])
                # result.append(gps[i + 1] + [current_v] + [limit_speed])
                current_v=starts(current_v)
                sec_starts = sec_starts + 1
                if sec_starts >= random.randint(6,8):
                    sec_starts=0
                    flag_start=False
                    flag_normal_driving=True
            continue

        # 选择概率
        if flag_quick_change == False and flag_normal_acclerate == False and flag_normal_stops == False and flag_normal_driving == False:
            quick = random.randint(0, quick_range)
            normal = random.randint(0, normal_range)

        #正常行驶
        if flag_normal_driving or (normal != 1 and normal != 2 and quick!=2):
            if total_dis>=current_v:
                total_dis = 0
                result.append(gps[i+1] + [current_v])
                # result.append(gps[i + 1] + [current_v] + [limit_speed])
                sec_normal = sec_normal + 1
                if current_v>change_limitspeed(limit_speed_1):
                    current_v =stops(current_v)
                elif change_limitspeed(limit_speed_1)<15 and change_limitspeed(limit_speed_1)-current_v>5:
                    current_v =normal_starts(current_v)
                elif change_limitspeed(limit_speed_1)>15 and change_limitspeed(limit_speed_1)-current_v>8:
                    current_v =normal_starts(current_v)
                else:
                    current_v = normal_driving(current_v)
                if sec_normal >= random.randint(25,35):
                    sec_normal = 0
                    flag_normal_driving=False
            continue

        #加速
        if (normal==1) and quick!=2:
            if total_dis>=current_v:
                total_dis = 0
                result.append(gps[i+1] + [current_v])
                # result.append(gps[i + 1] + [current_v] + [limit_speed])
                sec_accelerate = sec_accelerate + 1
                flag_normal_acclerate = True
                if current_v>change_limitspeed(limit_speed_1):
                    current_v =stops(current_v)
                elif change_limitspeed(limit_speed_1) < 15 and change_limitspeed(limit_speed_1) - current_v > 5:
                    current_v =normal_starts(current_v)
                elif change_limitspeed(limit_speed_1)<15 and change_limitspeed(limit_speed_1)-current_v>8:
                    current_v =normal_starts(current_v)
                else:
                    current_v = normal_starts(current_v)
                if sec_accelerate >= random.randint(5,12):
                    sec_accelerate = 0
                    flag_normal_acclerate = False
                    flag_normal_driving = True
            continue

        #减速
        if normal==2 and quick!=2:
            if total_dis>=current_v:
                total_dis = 0
                result.append(gps[i+1] + [current_v])
                # result.append(gps[i + 1] + [current_v] + [limit_speed])
                sec_decelerate = sec_decelerate + 1
                flag_normal_stops = True
                if current_v>change_limitspeed(limit_speed_1):
                    current_v =stops(current_v)
                elif change_limitspeed(limit_speed_1) < 15 and change_limitspeed(limit_speed_1) - current_v > 5:
                    current_v =normal_starts(current_v)
                elif change_limitspeed(limit_speed_1)<15 and change_limitspeed(limit_speed_1)-current_v>8:
                    current_v =normal_starts(current_v)
                else:
                    current_v = normal_stops(current_v)
                if current_v <= 1:
                    current_v = 0
                    flag_stop = True
                    sec_decelerate = 0
                    flag_normal_stops = False
                    continue
                if sec_decelerate >= random.randint(5,12):
                    sec_decelerate = 0
                    flag_normal_stops = False
                    flag_normal_driving = True
            continue

        #急加速 急刹车
        if quick ==2:
            if total_dis>=current_v:
                total_dis = 0
                result.append(gps[i + 1] + [current_v])
                # result.append(gps[i + 1] + [current_v] + [limit_speed])
                sec_quick = sec_quick + 1
                flag_quick_change = True
                if v_quick_change == 1 or current_v > limit_speed_1:
                    if v_quick_change != 2:
                        current_v = quick_stops(current_v)
                        v_quick_change = 1
                    else:
                        current_v = quick_starts(current_v)
                else:
                    current_v = quick_starts(current_v)
                    v_quick_change = 2
                if sec_quick >= random.randint(2,3):
                    v_quick_change = 0
                    sec_quick = 0
                    flag_quick_change = False
                    flag_normal_driving = True
                    if current_v<3:
                        flag_stop=True


    # 写入GPS数据到文件
    for i in range(len(result)):
        pos_id = pos_id + 1
        time = time + datetime.timedelta(seconds=1)
        result[i] = [pos_id] + [trip_id] + result[i] + [time]
        write_csv(result[i],result_gps_filename)
    return pos_id,time,trip_id


#上传csv方法
def upload_csv(result_gps_filename,result_trips_filename):
    now = datetime.datetime.now()
    remotefile = '/carson/test_upload/'+now.strftime('%Y-%m-%d-%H-%M-%S') #按当前时间新建一个文件夹
    client.makedirs(remotefile)
    client.upload(remotefile, result_gps_filename)
    client.upload(remotefile, result_trips_filename)

# 连接hdfs
client = Client("http://10.13.0.80:9870/", root="/", timeout=10000, session=False)
upload_file_path='E:\\Python\\Cardata\\upload' #本地文件位置


if __name__ == '__main__':
    file_count = 2 #生成文件数
    road_count = 2 #使用路段数 段
    car_count = 2 #生成车辆数 无限制


    for car in range(car_count):  # 车辆数循环
        trip_id = 1
        time = datetime.datetime.now()

        for file in range(file_count):  # 一辆车 生成多个文件
            position_result = []
            trip_result = []
            result_gps_filename = 'upload/position-car' + str(car+1) +'-file-'+str(file+1)+'.csv'
            beaglebone_id = car + 1
            pos_id = 0

            #生成position表
            for road in range(road_count): #路段循环
                initial_gps_filename = 'roadGPS/road_'+str(road+1)+'.csv' #路段gps集合
                limitspeed_filename = 'roadGPS/road_'+str(road+1)+'_limitspeed.csv' #路段限速集合

                #创建gps文件
                position_result =createGPS(trip_id,pos_id,time)
                trip_result.append([trip_id]+[beaglebone_id]+[time])
                pos_id = position_result[0]
                time = position_result[1] + datetime.timedelta(minutes=random.randint(720,2880))
                trip_id = position_result[2]+1
            #生成trips表
            for trip in range(len(trip_result)):
                result_trips_filename='upload/position-trips-car-'+str(beaglebone_id)+'-file-'+str(file+1)+'.csv'
                write_csv(trip_result[trip], result_trips_filename)

            # 上传到hdfs服务器
            upload_csv(result_gps_filename,result_trips_filename)






