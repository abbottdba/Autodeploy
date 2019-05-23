# -*- coding: utf-8 -*-
# @Time    : 4/2/2018 10:34 AM
# @Author  : Abbott
# @Site    : 
# @File    : MongoHandler.py
# @Software: PyCharm

from omtools.cores.commons import *
from omtools.cores.logsutils import *
import datetime
from bson import ObjectId

from conf import settings


class MongoFunction:
    def __init__(self, query_data):
        self.source_mongodb = settings.mongodb_env

        self.commons = commons()

        self.logfile = 'mongo.logs'
        self.LoggingConf = CommonLogging(self.logfile)
        self.time_now = datetime.datetime.now()

        msg = 'task_time: {0}, task_info: {1}'.format(self.time_now, query_data)
        self.LoggingConf.logging_info(msg)

        self.db = query_data['db']
        self.table = query_data['table']
        self.project = query_data['project']
        self.type = query_data['type']
        self.query = query_data['query']
        self.taskId = query_data['task_id']

        self.mongodb_execute_conn = self.commons.mongo_conn_collection(
            self.commons.mongoconf.mongo_conn(self.commons.get_Mongodb_info[self.source_mongodb][self.db]), self.db,
            self.table)

    def backup_mongodb(self):

        mongodb_backup_conn = self.commons.mongo_conn_collection(
            self.commons.mongoconf.mongo_conn(self.commons.get_Mongodb_info[self.source_mongodb]['backup']), self.db,
            self.table)
        online_data = self.mongodb_execute_conn.find(self.query['condition'])
        online_data_count = self.mongodb_execute_conn.find(self.query['condition']).count()
        if online_data_count > 0:
            backup_insert = []
            for item in online_data:
                item['old_id'] = item['_id']
                item['backupTime'] = self.time_now
                del item['_id']
                backup_insert.append(item)
            mongodb_backup_conn.insert_many(backup_insert)
            newquery = self.query['condition'].copy()
            newquery['backupTime'] = self.time_now
            backup_data_count = mongodb_backup_conn.find(newquery).count()
            msg = 'task_id: {0}, online_data_count: {1}, backup_data_count: {2}'.format(self.taskId, online_data_count,
                                                                                        backup_data_count)
            self.LoggingConf.logging_info(msg)
            if online_data_count != backup_data_count:
                msg = 'task_id: {0}, backup failed, delete backup first, backup again.'.format(self.taskId,
                                                                                               online_data_count,
                                                                                               backup_data_count)
                self.LoggingConf.logging_info(msg)
                mongodb_backup_conn.delete_many(newquery)
                self.backup_mongodb()
            status = 200
            return {'status': status, 'msg': msg}
        else:
            msg = 'task_id: {0}, matched_count: {1}, backup failed.'.format(self.taskId, online_data_count)
            self.LoggingConf.logging_warning(msg)
            status = 500
            return {'status': status, 'msg': msg}

    def find_query(self, conn, query):
        status = 200
        try:
            print(query['condition'])
            result = conn.find(query['condition'])
            # if query['property'] is None:
            #     result = conn.find(query['condition'])
            # else:
            #     result = conn.find(query['condition'], query['property'])
            msg = 'task_id: {0}, status: {1}, result: {2}'.format(self.taskId, status, result)
            self.LoggingConf.logging_info(msg)
            return {'status': status, 'msg': 'Success', 'result': result}
        except Exception as e:
            print(Exception, e)
            status = 500
            msg = 'task_id: {0}, status: {1}, exception: {2}-{3}'.format(self.taskId, status, Exception, e)
            self.LoggingConf.logging_error(msg)
            return {'status': status, 'msg': msg}

    def update_query(self, conn, query):
        status = 200
        try:
            if query['property'] == True:
                result = conn.update_many(query['condition'], query['set'])
            else:
                result = conn.update(query['condition'], query['set'])

            msg = 'task_id: {0}, status: {1}, matched_count: {2}, modified_count: {3}'.format(self.taskId, status,
                                                                                              result.matched_count,
                                                                                              result.modified_count)
            self.LoggingConf.logging_info(msg)
            return {'status': status, 'msg': msg}
        except Exception as e:
            status = 500
            msg = 'task_id: {0}, status: {1}, exception: {2}-{3}'.format(self.taskId, status, Exception, e)
            self.LoggingConf.logging_error(msg)
            return {'status': status, 'msg': msg}

    def insert_query(self, conn, query):
        conn.insert(query['condition'])

    def delete_query(self, conn, query):
        conn.delete(query['condition'])

    def execute_mongodb(self):
        if self.type == "update":
            backup_result = self.backup_mongodb()
            if backup_result['status'] == 200:
                result = self.update_query(self.mongodb_execute_conn, self.query)
                return result
            else:
                return backup_result
        elif self.type == "find":
            result = self.find_query(self.mongodb_execute_conn, self.query)
            return result
        elif self.type == "insert":
            pass
        else:
            pass


if __name__ == '__main__':
    query = {'db': 'logsdb', 'table': 'proposal', 'project': '', 'type': 'update',
             'query': {'condition': {'a': {'$in': ['1']}}, 'set': {'$set': {'b': '1'}}, 'property': True}}

    query = {'query': {'condition': {'proposalId': {'$in': ['234234']}}, 'property': True,
                       'set': {'$set': {'status': 'Success'}}}, 'table': 'proposal', 'type': 'update', 'project': '',
             'db': 'logsdb', 'task_id': 1}

    query = {'db': 'logsdb', 'table': 'playerConsumptionRecord', 'type': 'find', 'project': '', 'task_id': 154,
             'query': {'condition': {'orderNo': 'AG-180519001250193'}, 'set': {}, 'property': None}}

    query = {'db': 'logsdb', 'table': 'playerConsumptionRecord', 'type': 'find', 'project': '', 'task_id': 154,
             'query': {'createTime': {'$lt': datetime.datetime(2018, 5, 24, 4, 0), '$gte': datetime.datetime(2015, 5, 20, 4, 0)}, 'playerId': "ObjectId('5afd2f37f82f900010bef38c')"}}

    query = {'db': 'logsdb', 'table': 'playerConsumptionRecord', 'type': 'find', 'project': '', 'task_id': 154,
             'query': {'condition': {'createTime': {'$lt': datetime.datetime(2018, 5, 24, 4, 0),
                                      '$gte': datetime.datetime(2015, 5, 20, 4, 0)},
                                     'playerId': ObjectId('5866130dcdd5d001b7f164c4')
                                     } }
             }

    # query = {'db': 'logsdb', 'table': 'proposal', 'project': '', 'type': 'find',
    #          'query': {'condition': {'a': {'$in': ['1']}}, 'set': None, 'property': None}}
    MongoFunction(query).execute_mongodb()
