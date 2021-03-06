import requests
import random


request_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'DNT': '1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/67.0.3396.62 Safari/537.36'
}
# http://icanhazip.com/  http://httpbin.org/ip

proxy = [
    '61.135.217.7:80',
    '222.182.121.246:8118',
    '118.190.95.35:9001',
    '61.184.109.33;61320',
    '116.77.204.2:80',
    '60.216.101.46:59351',
    '183.159.90.14:18118',
    '112.98.126.100:41578',
    '180.168.13.26:8000',
    '180.118.241.94:61234',
    '175.148.78.174:1133',
    '115.46.73.58:8123',
    '175.155.24.39:808',
    '42.48.118.106:50038',
    '110.86.15.46:58945',
    '175.155.24.41:808',
    '59.32.37.112:61234',
    '171.38.79.36:8123',
    '122.115.78.240:38157',
    '116.192.171.51:48565',
    '61.138.33.20:808',
    '115.151.2.154:808',
    '175.175.219.97:1133',
    '59.32.37.82:8010',
    '171.37.162.104:8123',
    '115.46.71.44:8123',
    '110.73.6.199:8123',
    '182.88.135.96:8123',
    '49.85.4.155:43193',
    '60.179.40.16:808',
    '36.99.207.234:35618',
    '171.12.165.136:808',
    '49.85.3.191:30718',
    '123.161.152.173:22694',
    '119.5.1.21:808',
    '111.160.236.84:39692',
    '221.214.180.122:33190',
    '175.155.24.48:808',
    '115.29.200.195:808',
    '180.122.150.247:26055',
    '49.85.7.132:21026',
    '222.186.45.132:61374',
    '219.136.252.124:53281',
    '1.195.60.132:8118',
    '182.88.165.7:8123',
    '124.235.181.175:80',
    '180.118.241.187:808',
    '115.46.72.171:8123',
    '171.37.159.106:8123',
    '114.225.168.235:53128',
    '111.72.154.240:53128',
    '59.32.37.28:8010',
    '175.155.24.57:808',
    '59.32.37.134:8010',
    '119.5.0.18:808',
    '122.237.104.9:80',
    '114.225.171.173:53128',
    '175.148.75.246:1133',
    '119.5.1.33:808',
    '182.88.128.227:8123',
    '118.249.49.12:8118',
    '115.46.68.69:8123',
    '119.5.1.42:808',
    '171.37.158.178:8123',
    '121.31.176.201:8123',
    '121.31.193.254:8123',
    '119.5.1.51:808',
    '182.88.135.131:8123',
    '119.5.0.4:808',
    '121.31.156.98:8123',
    '210.72.14.142:80',
    '124.113.251.3:8010',
    '58.49.15.94:42821',
    '115.46.97.85:8123',
    '123.162.168.192:40274',
    '115.46.67.89:8123',
    '182.91.67.224:8123',
    '202.103.12.30:60850',
    '59.32.37.151:3128',
    '61.157.206.186:59007'




]
# try:
# #     # response1 = requests.get('http://icanhazip.com/',proxies={"http":"118.190.95.35:9001"})
# #     # response1 = requests.get('http://icanhazip.com/', proxies={"http": "http://61.138.33.20:808"})
# #     # response1 = requests.get('http://icanhazip.com/', proxies={"http": "175.148.78.174:1133"})
#       response1 = requests.get('http://www.baidu.com', proxies={"http": "116.77.204.2:80"})
# #     r = requests.get('https://s.weibo.com/', proxies={"http": "121.69.37.6:9797"})
#       print(response1.text)
# #     # print(response2.text)
# except:
#     print ('connect failed')
# else:
#     print ('success')

usable = []
for i in range(len(proxy)):
    try:
        code = requests.get('https://s.weibo.com/', proxies={"http": proxy[i]}).status_code
        if int(code)==200:
            print(proxy[i]+'可用')
            usable.append(proxy[i])
    except Exception as e:
        print(e)
        print(proxy[i]+'不可用')
print(len(proxy))
# filename = 'IP.txt'
# print(len(usable))
# with open(filename,'a') as f: # 如果filename不存在会自动创建， 'w'表示写数据，写之前会清空文件中的原有数据！
#     for i in range(len(usable)):
#         f.write(usable[i]+'\n')

