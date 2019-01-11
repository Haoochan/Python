import threading
import time

"""重新定义带返回值的线程类"""


class MyThread(threading.Thread):
    def __init__(self, func, args=()):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None

#
# """测试函数，计算两个数之和"""
#
#
# def fun():
#     time.sleep(1)
#     return 1
#
#
# li = []
# sum = 0
# for i in range(4):
#     t = MyThread(fun)
#     li.append(t)
#     t.start()
# for t in li:
#     t.join()  # 一定要join，不然主线程比子线程跑的快，会拿不到结果
#     sum = sum + t.get_result()
#     print(t.get_result())
# print(sum)