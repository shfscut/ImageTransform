
from threading import Thread
import threading
import time
# def count(n):
#     while n:
#         n-=1
#         print(n)
#         time.sleep(1)
#
# t=Thread(target=count, args=(10, ))
# t.start()
# t.join()

# class CountDownThread(Thread):
#     def __init__(self,n):
#         super().__init__()
#         self.n=n
#
#     def run(self):
#         while self.n>0:
#             print('T-minus', self.n)
#             self.n -= 1
#             time.sleep(2)
#
# c=CountDownThread(5)
# c.start()
from time import sleep

def now():
    return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

def test(nloop, nsec):
    print ('start loop', nloop, 'at:', now())
    sleep(nsec)
    print ('loop', nloop, 'done at:', now())

def main():
    print ('starting at:',now())
    threadpool = []

    for i in range(10):
        th = threading.Thread(target=test, args=(i, 2))
        threadpool.append(th)

    for th in threadpool:
        th.start()

    # for th in threadpool:
    #     threading.Thread.join(th)

    print ('all Done at:', now())

if __name__ == '__main__':
    main()