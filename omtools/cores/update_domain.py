import pickle as pickol
import os, sys, redis, platform
from pprint import pprint
import json
import django

if platform.system() == 'Linux':
    sys.path.append('/app/project/AutoDeploy')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AutoDeploy.settings")
django.setup()

from cmdb import models as CMDB_MODELS
from omtools import models as OMTOOLS_MODELS
from repository import models as REPOSITORY_MODELS

class DPS_DATA(object):
    def __init__(self,host,port,dbindex,password=None):
        self.__redishost = redis.StrictRedis(host=host,port=port,db=dbindex,password=password);
        self.app_map = {
            'XBET': 'XBET',
            'BBET8': 'BBET8',
            'RUIBO': 'RUIBO',
            'BBETASIA': 'BBETASIA',
            'BOLEBA/JINSHENG': 'JINSHENG',
            'EU': 'EU',
            'HAOMEN': 'HAOMEN',
            'JINSHENG/TIANHE': 'TIANHE',
        }

    def getData_DPS(self):
        return pickol.loads(self.__redishost.get('_DOMAINMNGR_DPS_CACHE'))

if __name__ == '__main__':
    REDIS_HOST = '10.168.11.205'
    REDIS_PORT = 6379
    REDIS_DBINDEX = 0
    d = DPS_DATA(REDIS_HOST,REDIS_PORT, REDIS_DBINDEX)
    dic_data = d.getData_DPS()
    app_map = d.app_map
    ip_from_api = []
    ip_from_db = []
    domain_from_api = []
    domain_from_db = []
    domain_dic = {}
    for product_name, domain_data in dic_data.items():
        project_obj = REPOSITORY_MODELS.ProjectInfo.objects.filter(name = app_map.get(product_name))
        if project_obj:
            for ip, data in domain_data.items():
                server_obj = OMTOOLS_MODELS.ProductDomainsIPaddr.objects.get_or_create(ip_addr=ip)[0]
                #server_obj.domain.clear()
                for domain in data['domains']:
                    domain_obj = OMTOOLS_MODELS.ProductDomains.objects.get_or_create(domain=domain[0])[0]
                    domain_obj.project_id = project_obj[0]
                    domain_obj.save()
                    server_obj.domain.add(domain_obj)
                    domain_from_api.append(domain[0])

                # delete old domain.
                domain_from_db = [i.domain for i in server_obj.domain.all()]
                server_obj.domain.filter(domain__in=(set(domain_from_db) - set(domain_from_api))).delete()

                ip_from_api.append(ip)

    # use set to delete db old data
    ip_from_db = [i.ip_addr for i in OMTOOLS_MODELS.ProductDomainsIPaddr.objects.all()]
    #domain_from_db = [i.domain for i in OMTOOLS_MODELS.ProductDomains.objects.all()]
    OMTOOLS_MODELS.ProductDomainsIPaddr.objects.filter(ip_addr__in=(set(ip_from_db) - set(ip_from_api))).delete()
    #OMTOOLS_MODELS.ProductDomains.objects.filter(domain__in=(set(domain_from_db) - set(domain_from_api))).delete()

