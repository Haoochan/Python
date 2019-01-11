from hdfs.client import *
import datetime
import os
test_file_path='E:\\GitHub\\Python\\test'

if __name__=='__main__':


    client = Client("http://10.13.0.80:9870/",root="/",timeout=10000,session=False)
    lists = os.listdir(test_file_path)
    print(lists)
    client.upload('/carson/test_upload',test_file_path+'\\'+lists[0])
    # os.remove(test_file_path+'\\'+'test.txt')


