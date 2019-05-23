from bson.objectid import ObjectId
import datetime
from pymongo.errors import AutoReconnect
import platform, os, sys
if platform.system() == 'Linux':
    sys.path.append('/app/project/AutoDeploy')
import json
import django
from pymongo import MongoClient
from omtools.cores import redis_handler
from omtools.cores import MongoHandler
from django.db import connections

from conf import settings


class MissionHandler:
    def __init__(self):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AutoDeploy.settings")
        django.setup()

    def __close_old_connections(self):
        for conn in connections.all():
            conn.close_if_unusable_or_obsolete()

    def get_mission_from_db(self, mission_id):
        self.__close_old_connections()
        from omtools import models as OMTOOLS_MODELS
        data_from_db = OMTOOLS_MODELS.MongodbMission.objects.get(id=mission_id)
        return data_from_db

    def post_api(self, mission_obj):
        m_db = mission_obj.database
        m_document = mission_obj.document
        m_find = mission_obj.find
        m_type = mission_obj.get_op_type_display()
        m_update = mission_obj.update
        m_multi_tag = mission_obj.multi_tag

        query = {
            'db': m_db,
            'table': m_document,
            'project': '',
            'type': m_type,
            'query': {
                #'condition': json.loads(m_find),
                #'set': json.loads(m_update) if m_update else {},
                'condition': eval(m_find),
                'set': eval(m_update),
                'property': m_multi_tag,
            },
            'task_id': mission_obj.id
        }

        result = MongoHandler.MongoFunction(query).execute_mongodb()

        if result['status'] == 200:
            mission_obj.status = 1
        elif result['status'] == 500:
            mission_obj.status = 3

        if m_type == 'update':
            mission_obj.op_detail = result['msg']
        elif m_type == 'find':
            if result['status'] == 200:
                # put result data to file.
                f = open('%s/web/static/download/mongo_data/%s.txt' %(settings.project_path, mission_obj.id), 'w')
                result_from_api = list(result['result'])
                if result_from_api:
                    if len(result_from_api) >= 10000:
                        f.write('query data can not more than 10000 rows.')
                    else:
                        for line in result_from_api:
                            f.write('%s\n' % str(line))
                else:
                    f.write('[]')
                f.close()
                mission_obj.op_detail = 'http://cmdb.omtools.me/static/download/mongo_data/%s.txt' % mission_obj.id
            else:
                mission_obj.op_detail = result['msg']

        mission_obj.save()

if __name__ == '__main__':
    redis_queue = redis_handler.RedisQueue('mongodb')
    while True:
        mission_from_redis = redis_queue.get_wait()
        mission_id = int(mission_from_redis[1])
        mission_handler = MissionHandler()
        mission_obj = mission_handler.get_mission_from_db(mission_id)
        mission_handler.post_api(mission_obj)