from django.test import TestCase

# Create your tests here.

import queue
import threading


class ThreadPool(object):

    def __init__(self, max_num=20):
        self.queue = queue.Queue(max_num)
        for i in range(max_num):
            self.queue.put(threading.Thread)

    def get_thread(self):
        return self.queue.get()

    def add_thread(self):
        self.queue.put(threading.Thread)

pool = ThreadPool(10)

def func(arg, p):
    print(arg)
    import time
    time.sleep(2)
    p.add_thread()

threading_pool = []
for times in range(0, for_times):
    th = threading.Thread(target=mission, args=(start, savelimit,))
    threading_pool.append(th)
    if len(threading_pool) == self.thread_max_limit or times == for_times - 1:
        for th in threading_pool:
            th.start()

        for th in threading_pool:
            th.join()

        threading_pool = []


for i in range(30):
    thread = pool.get_thread()
    t = thread(target=func, args=(i, pool))
    t.start()
