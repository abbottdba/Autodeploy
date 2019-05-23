# -*- coding: utf-8 -*-
# @Time    : 10/2/2017 10:20 AM
# @Author  : Abbott
# @Site    : 
# @File    : commons.py
# @Software: PyCharm


from omtools.cores.mongoconf import *
from decimal import *
import re
import threading
import hashlib
import os
import time
import signal

import pymongo
from dateutil.relativedelta import relativedelta

from conf import settings


class commons:
    """
    项目所有公共方法或者信息
    """

    def __init__(self):
        self.mongoconf = mongo_connect()



    def mongo_conn_collection(self, conn, db, collection):
        """
        连接mongo具体表的方法
        :param conn: 从Get_Mongodb_info获取要连接的mongo的dict
        :param db: 要连接的库
        :param collection: 要连接的表
        :return: 已经认证连接到表的class
        """

        return conn[db][collection]


    @property
    def get_Mongodb_info(self):
        """
        获取mongodb连接信息，再使用前请先和dba确认权限，ip，用户等信息是否正确，不正确请更新后再使用
        :return: mongo连接信息字典
        """
        conn_mongo = {
            "online": {"logsdb": dict(host='10.168.11.117', user='root', passwd='70f30d42783f69d0a3a907eaed8ca0eb', port=27018),
                       "backup": dict(host='10.168.11.141', user='root', passwd='70f30d42783f69d0a3a907eaed8ca0eb', port=27018),
                       "admindb": dict(host='10.168.11.135', user='root', passwd='70f30d42783f69d0a3a907eaed8ca0eb', port=27019),
                       "playerdb": dict(host='10.168.11.138', user='root', passwd='70f30d42783f69d0a3a907eaed8ca0eb', port=27020)},
            "cstest": {"logsdb": dict(host='192.168.10.230', user='mysqltomongo', passwd='mongopwd', port=27018),
                     "backup": dict(host='192.168.10.230', user='mysqltomongo', passwd='mongopwd', port=27021),
                     "admindb": dict(host='192.168.10.230', user='mysqltomongo', passwd='mongopwd', port=27019),
                     "playerdb": dict(host='192.168.10.230', user='mysqltomongo', passwd='mongopwd', port=27020)}
        }
        return conn_mongo

    @property
    def mongo_db_table_info(self):
        """
        mongo信息表库和表对应关系
        :return: 库表对应字典
        """
        db_table_info = {
            "platform": {"db": "admindb", "collection": "platform"},
            "bankinfo": {"db": "", "collection": ""},
            "partnerlevel": {"db": "admindb", "collection": "partnerLevel"},
            "playerlevel": {"db": "admindb", "collection": "playerLevel"},
            "playerinfo": {"db": "playerdb", "collection": "playerInfo"},
            "playertopuprecord": {"db": "logsdb", "collection": "playerTopUpRecord"},
            "gameprovider": {"db": "admindb", "collection": "gameProvider"},
            "game": {"db": "admindb", "collection": "game"},
            "playerconsumptionrecord": {"db": "logsdb", "collection": "playerConsumptionRecord"},
            "partner": {"db": "playerdb", "collection": "partner"},
            "logsbackup": {"db": "logstmp", "collection": "playerConsumptionRecord_bak"},
            "logssum": {"db": "logstmp", "collection": "playerConsumptionRecord_sum"}

        }

        return db_table_info

    def Get_platformId(self, conn, project):
        """
        获取platformid
        :param project:在__init__方法里可以定义，也可以后期添加一个配置文件
        :return: platform objectid
        """
        platform = self.mongo_conn_collection(conn, self.mongo_db_table_info["platform"]["db"], self.mongo_db_table_info["platform"]["collection"])
        return platform.find_one({"name": project})["_id"]

    @property
    def get_UTC_time(self):
        """
        转化为格林威治时间
        :return: 返回需要转化为格林威治时间的间隔小时
        """

        return datetime.timedelta(hours=8)


    def md5(self, str):
        md5 = hashlib.md5()
        md5.update(str)
        return md5.hexdigest()


