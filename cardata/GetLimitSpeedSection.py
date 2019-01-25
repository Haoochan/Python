import csv

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
        f_csv.writerow((result))


#注意使用本程序获取所有限速段的前提条件是 已经手动清理完 限速的数据
#可以先不生成limitspeedAll文件 只输出count 看看是否清理干净
if __name__ == '__main__':
    limitspeed_result_filename = 'roadGPS/limitspeedAll.csv'
    for k in range(20):
        limitspeed_filename = 'roadGPS/road_'+str(k+1)+'_limitspeed-2.csv'  # 路段限速集合
        gps=get_csv(limitspeed_filename)
        limit_speed =0
        limit_speed_result =[]
        count = 0
        for i in range(len(gps)):
            if gps[i][2]!=limit_speed:
                limit_speed=gps[i][2]
                a = i
                count = count + 1
                for j in range(200):
                    try:
                        temp = []
                        temp.append(gps[a+j][0])
                        temp.append(gps[a+j][1])
                        temp.append(gps[a+j][2])
                        limit_speed_result.append(temp)
                        # print(gps[a+j][0],gps[a+j][1],gps[a+j][2])
                    except:
                        continue

        for i in range(len(limit_speed_result)):
            write_csv(limit_speed_result[i],limitspeed_result_filename)

        print(count)
