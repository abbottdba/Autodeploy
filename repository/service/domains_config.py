import json
from django.db.models import Q
from repository import models
from utils.pager import PageInfo
from utils.response import BaseResponse
from django.http.request import QueryDict

from .base import BaseServiceList
from repository import models as repository_models
from cmdb import models as CMDB_MODELS


class ServerDomains(BaseServiceList):
    def __init__(self):
        pass

    @staticmethod
    def get_server_domains(server_id):
        response = BaseResponse()
        try:
            response.data = models.Applications.objects.filter(id=server_id).first()

        except Exception as e:
            response.status = False
            response.message = str(e)
        return response

    @staticmethod
    def get_server_domains_json(server_id):
        response = BaseResponse()

        try:
            server_domains_list = repository_models.WebConfigDomains.objects.filter(app_id=server_id).values(
                                                                                              'id',
                                                                                              'domain',
                                                                                              'ssl_tag',
                                                                                              'app_id__name',
                                                                                              'app_id__project_id__name',
                                                                                              'memo').order_by("-id")

            response.data = list(server_domains_list)
        except Exception as e:
            print(Exception, e)
            response.status = False
            response.message = str(e)
        return response

    def add_domain(request):
        response = BaseResponse()
        try:
            response.error = {}
            post_dict = QueryDict(request.body, encoding='utf-8')

            app_id = post_dict.get('app_id')
            domain_url = post_dict.get('domain_url')
            domain_memo = post_dict.get('domain_memo')

            add_to_db = repository_models.WebConfigDomains(
                app_id_id = app_id,
                domain = domain_url,
                memo = domain_memo
            )
            add_to_db.save()

        except Exception as e:
            print(Exception, e)
            response.status = False
            response.message = str(e)
        return response

    def delete_domain(request):
        response = BaseResponse()
        try:
            response.error = {}
            post_dict = QueryDict(request.body, encoding='utf-8')
            domain_id = post_dict.get('domain_id')

            data_from_db = repository_models.WebConfigDomains.objects.get(id=domain_id)
            data_from_db.delete()

        except Exception as e:
            print(Exception, e)
            response.status = False
            response.message = str(e)
        return response

    def update_domain(request):
        response = BaseResponse()
        try:
            response.error = {}
            post_dict = QueryDict(request.body, encoding='utf-8')

            print(post_dict)

            domain_id = post_dict.get('domain_id')
            domain_url = post_dict.get('domain_url')
            domain_memo = post_dict.get('domain_memo')

            get_data_from_db = repository_models.WebConfigDomains.objects.get(id=domain_id)
            get_data_from_db.domain = domain_url
            get_data_from_db.memo = domain_memo
            get_data_from_db.save()

        except Exception as e:
            print(Exception, e)
            response.status = False
            response.message = str(e)
        return response

    def get_domain_by_id(request):
        try:
            response = BaseResponse()
            domain_id = request.GET.get('domain_id')
            get_edit_domain_data = repository_models.WebConfigDomains.objects.filter(id=domain_id).values("id", "domain", "ssl_tag", "memo")
            response.data = list(get_edit_domain_data)
            return response.data
        except Exception as e:
            print(Exception, e)

    def get_urlmaps_groups_by_id(request):
        response = BaseResponse()
        try:
            response.error = {}
            group_type = request.GET.get('group_type')
            group_id = request.GET.get('group_id')
            urlmaps_id = request.GET.get('urlmaps_id')

            urlmaps_obj = repository_models.UrlConfigHandler.objects.filter(id=urlmaps_id).values()
            if group_type == 'cloud':
                instance_in_group = CMDB_MODELS.Asset.objects.filter(instances__id=group_id).values('id', 'server__ipaddress')
                instance_in_urlmaps = CMDB_MODELS.Asset.objects.filter(urlconfighandler_cloud__id=urlmaps_id).values('id', 'server__ipaddress')
            elif group_type == 'forward':
                instance_in_group = CMDB_MODELS.Asset.objects.filter(instances__id=group_id).values('id', 'server__ipaddress')
                instance_in_urlmaps = CMDB_MODELS.Asset.objects.filter(urlconfighandler_forward__id=urlmaps_id).values('id', 'server__ipaddress')
            elif group_type == 'docker':
                instance_in_group = CMDB_MODELS.Asset.objects.filter(instances__id=group_id).values('id','server__ipaddress')
                instance_in_urlmaps = CMDB_MODELS.DockerInstance.objects.filter(urlconfighandler_docker__id=urlmaps_id).values('id', 'asset__server__ipaddress', 'port')
                print(instance_in_urlmaps)

            response.urlmaps_obj = list(urlmaps_obj)
            response.left_select_list = list(instance_in_group)
            response.right_select_list = list(instance_in_urlmaps)

        except Exception as e:
            print(Exception, e)
            response.status = False
            response.message = str(e)
        return response

    def update_urlmaps_groups(request):
        response = BaseResponse()
        try:
            response.error = {}
            post_dict = QueryDict(request.body, encoding='utf-8')
            urlmaps_id = post_dict.get('urlmaps_id')
            instance_list = post_dict.getlist('instance_list')
            group_type = post_dict.get('group_type')

            urlmaps_obj = repository_models.UrlConfigHandler.objects.get(id=urlmaps_id)

            if group_type == 'cloud':
                urlmaps_obj.cloud.clear()
                for instance_id in instance_list:
                    urlmaps_obj.cloud.add(CMDB_MODELS.Asset.objects.get(id=instance_id))
            elif group_type == 'forward':
                urlmaps_obj.forward.clear()
                for instance_id in instance_list:
                    urlmaps_obj.forward.add(CMDB_MODELS.Asset.objects.get(id=instance_id))
            elif group_type == 'docker':
                urlmaps_obj.docker.clear()
                for instance_id in instance_list:
                    urlmaps_obj.docker.add(CMDB_MODELS.DockerInstance.objects.get(id=instance_id))

        except Exception as e:
            print(Exception, e)
            response.status = False
            response.message = str(e)
        return response
