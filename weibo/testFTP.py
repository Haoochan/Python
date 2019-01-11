import ftplib
import datetime
import os
#
now = datetime.datetime.now()
print(now)
def upload_csv(keyword):
    latest_file = new_file(test_file_path)
    if latest_file!=None:
        host = '10.13.0.80'
        username = 'csv_uploader'
        password = '123456'
        ftp = ftplib.FTP(host)  # 实例化FTP对象
        ftp.login(username, password)  # 登录
        ftp.encoding = 'utf-8'
        # try:
        #     ftp.mkd(keyword)
        # except:
        #     print('目录已存在')
        # ftp.cwd(keyword)
        file_remote = latest_file.split('\\')[-1] #上传到服务器的文件名
        file_local = latest_file #文件的本地路径
        bufsize = 1024  # 设置缓冲器大小
        fp = open(file_local, 'rb')
        ftp.storbinary('STOR ' + file_remote, fp, bufsize)

        now = datetime.datetime.now()
        print(now)
        ftp.dir()
        ftp.quit()
#返回的是全路径
def new_file(test_file_path):
    lists = os.listdir(test_file_path)                                    #列出目录的下所有文件和文件夹保存到lists
    print(lists)
    if len(lists)>0:
        lists.sort(key=lambda fn:os.path.getmtime(test_file_path + "\\" + fn))#按时间排序
        file_new = os.path.join(test_file_path,lists[-1])                     #获取最新的文件保存到file_new 全路径
        print(file_new)
        return file_new
    else:
        print('文件为空')
        return None


if __name__=='__main__':
    keyword = 'test'
    # test_file_path='E:\\GitHub\\Python\\'+keyword#目录地址
    test_file_path = 'E:\\GitHub\\Python\\test'  # 目录地址
    # latest_file=new_file(test_file_path)
    upload_csv(keyword)
    # new_file(test_file_path)