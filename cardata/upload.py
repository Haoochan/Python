from hdfs.client import *
import datetime

#上传csv方法 上传到hdfs指定目录 remotefile
def upload_csv(lists):
    #每次上传在服务器新建一个文件夹
    now = datetime.datetime.now()
    remotefile = '/carson/test_upload/'+now.strftime('%Y-%m-%d-%H-%M-%S') #按当前时间在远程目录新建一个文件夹
    client.makedirs(remotefile)
    for i in range(len(lists)):
        #拼接文件名
        filename='upload/'+lists[i]
        client.upload(remotefile, filename)

# 连接hdfs
client = Client("http://10.13.0.80:9870/", root="/", timeout=10000, session=False)
upload_file_path='E:\\Python\\Cardata\\upload' #本地文件位置

if __name__ == '__main__':
    #读取文件夹下所有文件
    lists = os.listdir(upload_file_path)
    #上传到服务器
    upload_csv(lists)

