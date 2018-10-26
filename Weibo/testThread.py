import threading
import time
import datetime

def test1():
    for i in range(5):
        print('test1')
    return 1


def test2():
    for i in range(5):
        print('test2')
    return 1

threads = []
t1 = threading.Thread(target=test1)
threads.append(t1)
t2 = threading.Thread(target=test2)
threads.append(t2)

if __name__=='__main__':
    now = datetime.datetime.now()
    print(now)
    t1.setDaemon(True)
    t1.start()
    t2.setDaemon(True)
    t2.start()
    sum =test1()+test2()
    t1.join()
    t2.join()




    print('----------')
    now = datetime.datetime.now()
    print(now)

