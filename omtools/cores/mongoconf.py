# -*- coding: utf-8 -*-
# @Time    : 5/10/2017 10:56 AM
# @Author  : Abbott
# @Site    : 
# @File    : mongoconf.py
# @Software: PyCharm

from pymongo import MongoClient

class mongo_connect:
    """
    连接mongo的class
    """
    def mongo_conn(self, kwargs):
        """

        :param kwargs:mongo连接方式字典
        :return: mongo认证后的client，方便使用
        """
        client = MongoClient(kwargs['host'], kwargs['port'], maxPoolSize=1000, waitQueueMultiple=100)
        db_auth = client.admin
        db_auth.authenticate(kwargs['user'], kwargs['passwd'])
        return client
