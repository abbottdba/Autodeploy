
from conf import settings
import redis

class RedisQueue(object):
    def __init__(self, namespace, **redis_kwargs):
       self.__db= redis.Redis(host=settings.redis_host, port=settings.redis_port, db=settings.redis_db)
       self.key = namespace

    def qsize(self):
        return self.__db.llen(self.key)  # 返回队列里面list内元素的数量

    def put(self, item):
        self.__db.rpush(self.key, item)  # 添加新元素到队列最右方

    def get_wait(self, timeout=None):
        # 返回队列第一个元素，如果为空则等待至有元素被加入队列（超时时间阈值为timeout，如果为None则一直等待）
        item = self.__db.blpop(self.key, timeout=timeout)
        # if item:
        #     item = item[1]  # 返回值为一个tuple
        return item

    def get_nowait(self):
        # 直接返回队列第一个元素，如果队列为空返回的是None
        item = self.__db.lpop(self.key)
        return item

if __name__ == '__main__':
    import time

    q = RedisQueue('mongodb', host='10.168.11.54', port=6379, db=0)  # 新建队列名为rq
    while True:
        # q.put(i)
        # print("input.py: data {} enqueue {}".format(i, time.strftime("%c")))
        # time.sleep(1)
        print(q.get_wait())
        print(111)