import ftplib

host = '10.13.0.80'
username = 'csv_uploader'
password = '123456'
ftp = ftplib.FTP(host)  # 实例化FTP对象
ftp.login(username, password)  # 登录
ftp.encoding = 'utf-8'
ftp.cwd('test')
ftp.dir()
# ftp.rmd('test2')
ftp.delete('2018-10-25 14-40-58.280752泰国小老板紫菜好吃.csv')
# ftp.delete('2018-10-25 14-42-36.547578伊卡璐洗发露.csv')
# ftp.delete('2018-10-25 14-41-20.895014伊卡璐洗发露.csv')
ftp.dir()
ftp.quit()