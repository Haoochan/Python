from math import *
import csv
import random
import datetime
from hdfs.client import *


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

#读取限速道路gps 通过字典的方式读入csv文件数据 还没有完善
def get_limit_csv(filename):
    csv_file=csv.reader(open(filename,'r'))
    GPS = {}
    for i in csv_file:
        GPS[(i[0],i[1])]=i[2]
    return GPS


#写入生成的gps
def write_csv(result,filename):
    with open(filename, 'a', errors='ignore',newline='') as f:
        f_csv = csv.writer(f)
        f_csv.writerow((result))

#急加速 百度地图的标准是+-1.67 这里调大了一些
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

#限速120的 调低一点
def change_limitspeed(limitspeed):
    if limitspeed>=33:
        limitspeed = 27
    return limitspeed


#生成gps数据
def createGPS(trip_id,pos_id,time):
    gps = get_csv(initial_gps_filename)
    total_dis = 0
    current_v = 0
    sec_quick_start = 0 #急变速持续时间
    sec_quick_stop = 0  # 急减速持续时间
    sec_accelerate = 0 #普通加速持续时间
    sec_decelerate = 0 #普通减速持续时间
    sec_normal = 0 #正常行驶持续时间
    sec_starts =0 #启动持续时间
    sec_stops = 0 #trip即将结束减速时间
    sec_normal_in_stop = 0 #trip即将结束中匀速时间
    flag_quick_start = False #急加速
    flag_quick_stop = False  # 急减速
    flag_normal_acclerate = False #正常加速
    flag_normal_stops = False #正常减速
    flag_normal_driving = False #正常匀速行驶
    flag_stop = True #停车
    flag_start = False #停车后启动
    flag_break = False #trip即将结束的减速
    flag_end_normal = False #trip即将结束中的匀速
    quick_range = 100  # 急变速概率范围
    normal_range = 20  # 普通加减速概率范围
    result = [] #生成路段
    # 获取道路限速
    limitspeedcsv = get_csv(limitspeed_filename)
    # 添加开始位置gps
    result.append(gps[0]+[current_v])

    for i in range(len(gps) - 1):
        limit_speed = int(limitspeedcsv[i][2])/3.6

        #计算每两个点距离 并累加 用来跟速度比较
        dis = geodistance(float(gps[i][0]), float(gps[i][1]), float(gps[i + 1][0]), float(gps[i + 1][1]))
        total_dis = total_dis + dis

        #结束 减速停车 因为没有实现按照路程自然结束地去减速停车 所以最后一段路程强制减速到停车
        #改进的话可能就是加多一个变量是一直计算当前点与最后一个gps点的距离，当距离小于某个值，就令车进入结束减速停车阶段
        if i>= (len(gps) - 1-6000):
            #减速 但还没有停车
            if current_v>0:
                if total_dis>=current_v: #记录该gps点
                    total_dis = 0
                    result.append(gps[i+1] + [current_v])
                    b = random.randint(1,2)#随机 1是匀速 2是减速
                    #减速 持续2-4秒
                    if (b==2 or flag_break) and flag_end_normal==False:
                        flag_break = True
                        sec_stops = sec_stops + 1
                        current_v = stops(current_v)
                        if current_v < 0:
                            current_v = 0
                        if sec_stops>=random.randint(2,4):
                            sec_stops = 0
                            flag_break = False
                        continue
                    #匀速 持续4-6秒
                    if flag_break==False or flag_end_normal or b==1:
                        sec_normal_in_stop = sec_normal_in_stop +1
                        flag_end_normal = True
                        current_v=normal_driving(current_v)
                        if sec_normal_in_stop>=random.randint(4,6):
                            sec_normal_in_stop = 0
                            flag_end_normal = False
                    #有可能出现负数 置为0
                    if current_v < 0:
                        current_v=0
                continue
            else:#已停车 额外随机添加10-25个重复点 模拟停车但还没熄火离开状态
                for k in range(random.randint(10, 25)):
                    result.append(gps[i+1] + [0])
                break

        #停车  中途停车随后启动 没有实现红绿灯，路口等停车，因为获取不了红绿灯gps
        if flag_stop:
            if current_v>0:
                if total_dis>=current_v:#记录该gps点
                    total_dis = 0
                    result.append(gps[i+1] + [current_v])
                    current_v = normal_stops(current_v)
            if current_v<=0:
                current_v = 0
                #随机停车10-25秒
                stop_seconds = random.randint(10, 25)
                for j in range(stop_seconds):
                    result.append(gps[i] + [current_v])
                flag_stop = False
                #接启动
                flag_start = True
                current_v = normal_starts(current_v)
            continue

        #启动
        if flag_start:
            if total_dis>=current_v:
                total_dis = 0
                result.append(gps[i+1] + [current_v])#记录该gps点
                current_v=starts(current_v)
                sec_starts = sec_starts + 1
                if sec_starts >= random.randint(6,8):
                    sec_starts=0
                    flag_start=False
                    flag_normal_driving=True #启动后接匀速
            continue

        # 选择概率 根据概率 匀速，加速，减速，急加速，急减速
        if flag_quick_start == False and flag_normal_acclerate == False and flag_normal_stops == False and flag_normal_driving == False and flag_quick_stop==False:
            #quick = 1 急加速 quick = 2急减速 normal=1加速 normal=2减速
            quick = random.randint(0, quick_range) #急加速减速概率范围 0-120
            normal = random.randint(0, normal_range) #加速减速概率范围0-50  都不中的话就是匀速了

        #正常行驶
        if flag_normal_driving or (normal != 1 and normal != 2 and quick != 1 and quick != 2):
            if total_dis>=current_v:
                total_dis = 0
                result.append(gps[i+1] + [current_v]) #记录该gps点
                flag_normal_driving=True
                sec_normal = sec_normal + 1
                #超过限速 减速
                if current_v>change_limitspeed(limit_speed):
                    current_v =normal_stops(current_v)
                # 这两个elif 避免龟速 与限速值相差太远
                elif change_limitspeed(limit_speed)<15 and change_limitspeed(limit_speed)-current_v>5:
                    current_v =normal_starts(current_v)
                elif change_limitspeed(limit_speed)>15 and change_limitspeed(limit_speed)-current_v>8:
                    current_v =normal_starts(current_v)
                else:
                    current_v = normal_driving(current_v)
                #持续10-20秒
                if sec_normal >= random.randint(10,20):
                    sec_normal = 0
                    flag_normal_driving=False
            continue

        #加速
        if (normal==1) and quick!=2 and quick!=1:
            if total_dis>=current_v:
                total_dis = 0
                result.append(gps[i+1] + [current_v]) #记录该gps点
                sec_accelerate = sec_accelerate + 1
                flag_normal_acclerate = True
                # 超过限速 减速
                if current_v>change_limitspeed(limit_speed):
                    current_v = stops(current_v)
                else:
                    current_v = normal_starts(current_v)
                # 持续5-12秒
                if sec_accelerate >= random.randint(5,12):
                    sec_accelerate = 0
                    flag_normal_acclerate = False
                    flag_normal_driving = True #接一个匀速
            continue

        #减速
        if normal==2 and quick!=2 and quick!=1:
            if total_dis>=current_v:
                total_dis = 0
                result.append(gps[i+1] + [current_v]) #记录该gps点
                sec_decelerate = sec_decelerate + 1
                flag_normal_stops = True
                # 这两个elif 避免龟速 与限速值相差太远
                if change_limitspeed(limit_speed) < 15 and change_limitspeed(limit_speed) - current_v > 5:
                    current_v =normal_starts(current_v)
                elif change_limitspeed(limit_speed)<15 and change_limitspeed(limit_speed)-current_v>8:
                    current_v =normal_starts(current_v)
                else:
                    current_v = normal_stops(current_v)
                #当减速到某个值 触发停车
                if current_v <= 2:
                    current_v = 0
                    flag_stop = True
                    sec_decelerate = 0
                    flag_normal_stops = False
                    continue
                # 持续5-12秒
                if sec_decelerate >= random.randint(5,12):
                    sec_decelerate = 0
                    flag_normal_stops = False
                    flag_normal_driving = True #接一个匀速
            continue

        #急加速
        if quick == 2 and normal!=1 and normal!=2:
            if total_dis >= current_v:
                total_dis = 0
                result.append(gps[i + 1] + [current_v]) #记录该gps点
                sec_quick_start = sec_quick_start + 1
                flag_quick_start = True
                current_v = quick_starts(current_v)
                if sec_quick_start >= random.randint(2, 3):
                    sec_quick_start = 0
                    flag_quick_start = False
                    flag_normal_driving = True #接一个匀速
            continue

        # 急减速
        if quick == 1 and normal!=1 and normal!=2:
            if total_dis >= current_v:
                total_dis = 0
                result.append(gps[i + 1] + [current_v]) #记录该gps点
                sec_quick_stop = sec_quick_stop + 1
                flag_quick_stop = True
                current_v = quick_stops(current_v)
                if sec_quick_stop >= random.randint(2, 3):
                    sec_quick_stop = 0
                    flag_quick_stop = False
                    flag_normal_driving = True #接一个匀速
                    if current_v<2:
                        flag_stop=True
            continue

    # 写入GPS数据到文件
    for i in range(len(result)):
        pos_id = pos_id+1
        time = time + datetime.timedelta(seconds=1)
        #拼接结果 posid，tripid，longitude，latitude，altitude（海拔无法获取，用速度值暂代），time
        result[i] = [pos_id] + [trip_id] + result[i] + [time]
        write_csv(result[i],result_gps_filename)

    return pos_id,time,trip_id


#上传csv方法 上传到hdfs指定目录 remotefile
def upload_csv(result_gps_filename,result_trips_filename):
    now = datetime.datetime.now()
    remotefile = '/carson/test_upload/'+now.strftime('%Y-%m-%d-%H-%M-%S') #按当前时间在远程目录新建一个文件夹
    client.makedirs(remotefile)
    client.upload(remotefile, result_gps_filename)
    client.upload(remotefile, result_trips_filename)

# 连接hdfs
client = Client("http://10.13.0.80:9870/", root="/", timeout=10000, session=False)
upload_file_path='E:\\Python\\Cardata\\upload' #本地文件位置


if __name__ == '__main__':
    file_count = 1 #生成文件数
    road_count = 20 #使用路段数 段
    car_count = 1 #生成车辆数 无限制

    trip_id = 1 #放在这里 区别每段trip 放进去的话 每辆车都有1,2,3....个trip
    pos_id = 0
    flag=1

    print(datetime.datetime.now())

    #根据tripId 每个文件100个trip 生成740份trip文件
    for i in range(5):
        time = datetime.datetime.now()
        position_result = []
        result_gps_filename = 'upload/position'+str(flag)+'-file-'+'test.csv'
        # 生成position表
        for road in range(road_count):  # 路段循环
            initial_gps_filename = 'roadGPS/road_' + str(road + 1) + 'test.csv'  # 路段gps集合
            limitspeed_filename = 'roadGPS/road_' + str(road + 1) + '_limitspeed-2.csv'  # 路段限速集合
            # 创建gps文件
            position_result = createGPS(trip_id, pos_id, time)  # 用一个list装函数的返回值
            pos_id = position_result[0]
            #同一辆车的每段trip之间 随机间隔12-48小时
            time = position_result[1] + datetime.timedelta(minutes=random.randint(720, 2880))
            trip_id = position_result[2] + 1
            #100段trip生成1个文件
            if trip_id % 100 == 0:
                flag = flag + 1

    print(datetime.datetime.now())

    # for file in range(file_count):  # 生成多个文件(一台车对应一个)
    #
    #     for car in range(car_count):  # 车辆数循环
    #         time = datetime.datetime.now()
    #         position_result = []
    #         trip_result = []
    #         result_gps_filename = 'upload/position-car' + str(car+1) +'-file-'+str(file+1)+'.csv'
    #         beaglebone_id = car + 1 #对应demo的 其实是carid
    #         pos_id = 0
    #
    #         #生成position表
    #         for road in range(road_count): #路段循环
    #             initial_gps_filename = 'roadGPS/road_'+str(road+1)+'.csv' #路段gps集合
    #             limitspeed_filename = 'roadGPS/road_'+str(road+1)+'_limitspeed-2.csv' #路段限速集合
    #
    #             #创建gps文件
    #             position_result =createGPS(trip_id,pos_id,time) #用一个list装函数的返回值
    #             trip_result.append([trip_id]+[beaglebone_id]+[time])
    #             pos_id = position_result[0]
    #             time = position_result[1] + datetime.timedelta(minutes=random.randint(720,2880))
    #             trip_id = position_result[2]+1
            #生成trips表
            # for trip in range(len(trip_result)):
            #     result_trips_filename='upload/position-trips-car-'+str(beaglebone_id)+'-file-'+str(file+1)+'.csv'
            #     write_csv(trip_result[trip], result_trips_filename)

            # 上传到hdfs服务器
            # upload_csv(result_gps_filename,result_trips_filename)







