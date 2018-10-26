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
        code = requests.get('https://www.lagou.com', proxies={"http": proxy[i]}).status_code
        if int(code)==200:
            print(proxy[i]+'可用')
            usable.append(proxy[i])
    except Exception as e:
        print(e)
        print(proxy[i]+'不可用')

# filename = 'IP.txt'
# print(len(usable))
# with open(filename,'a') as f: # 如果filename不存在会自动创建， 'w'表示写数据，写之前会清空文件中的原有数据！
#     for i in range(len(usable)):
#         f.write(usable[i]+'\n')

