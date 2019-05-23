__author__ = 'Aaron'

from cmdb import models as cmdb_models
from omtools import models as OMTOOLS_MODELS
from utils.public_utils import business_node_top, business_user_filter
import json
import time

class ApiHandler:
    def __init__(self, request):
        self.request_data = request.body.decode('utf-8')
        self.request_json_data = json.loads(self.request_data)

        try:
            self.page = self.request_json_data['parameters']['page']
            self.limit = self.request_json_data['parameters']['limit']
            self.start_tag = self.page * self.limit - self.limit
            self.end_tag = self.page * self.limit
        except:
            self.page = None
            self.limit = None
            self.start_tag = None
            self.end_tag = None

        self.cmdb_data = cmdb_models.Asset.objects
        self.response_msg = ''

    '''
    接口提交字段验证
    '''
    def check_data_component(self):
        request_field = ['option', 'parameters', 'token', 'timestamp']
        key_list = []
        for key, value in self.request_json_data.items():
            key_list.append(key)
        if len(set(key_list) - set(request_field)) == 0 and len(set(request_field) - set(key_list)) == 0:
            return self.__check_token_data()
        else:
            self.response_msg = {'status': 500, 'msg': 'missing or error request parameters data, please check.'}
            return False

    '''
    接口token验证
    '''
    def __check_token_data(self):
        Token_STR = 'NEBB5oMQOPMpLTn6PneJKBDEMU0WeBxd'
        timeStamp = time.time()
        req_token = self.request_json_data.get('token')
        req_timestamp = self.request_json_data.get('timestamp')

        # 验证请求时间戳是否过期
        if not 10 > (int(timeStamp) - int(req_timestamp)) > -10:
            self.response_msg = {'status': 403, 'msg': 'The token for the request has expired.'}
            return False

        import hashlib
        md5_handler = hashlib.md5(str(Token_STR + req_timestamp).encode('utf-8'))

        if req_token == md5_handler.hexdigest():
            return True
        else:
            self.response_msg = {'status': 403, 'msg': 'Permission authentication failed, Please check token value.'}
            return False

    def __get_field_data(self):
        pass

    def __page_data_calculator(self):
        pass

    def __get_available_ip_from_nic(self, nic_list_objects):
        exclude_list = [None, '', '127.0.0.1']
        for nic_object in nic_list_objects:
            if nic_object.ipaddress not in exclude_list:
                return nic_object.ipaddress

        return '未知'

    def __formatting_json(self, source_data):
        items_list = []
        for objects in source_data:
            items_data = {}

            try:
                items_data['idc'] = objects.idc.name
            except:
                items_data['idc'] = '-'

            try:
                items_data['ip'] = objects.server.ipaddress
            except:
                items_data['ip'] = '-'

            try:
                items_data['sn'] = objects.sn
            except:
                items_data['sn'] = '-'

            items_data['asset_type'] = objects.get_device_type_id_display()

            try:
                items_data['manufactory'] = objects.server.manufactory
            except:
                items_data['manufactory'] = '-'

            try:
                items_data['model'] = objects.server.model
            except:
                items_data['model'] = '-'

            try:
                items_data['os_type'] = objects.server.os_type
            except:
                items_data['os_type'] = '-'

            try:
                items_data['os_version'] = objects.server.os_release
            except:
                items_data['os_version'] = '-'

            if objects.server.hostname:
                items_data['hostname'] = objects.server.hostname
            else:
                items_data['hostname'] = '-'

            if objects.server.configuration:
                items_data['configuration'] = objects.server.configuration
            else:
                items_data['configuration'] = '-'

            try:
                items_data['business'] = self.__get_business_full_name(objects.business_unit)
            except Exception as e:
                items_data['business'] = '-'

            try:
                items_data['admin'] = self.__get_business_admin_list(objects.business_unit)
            except Exception as e:
                print(e)
                items_data['admin'] = []

            try:
                items_data['status'] = objects.get_device_status_id_display()
            except:
                items_data['status'] = '-'

            try:
                items_data['function'] = [i.name for i in objects.tag.all()]
            except:
                items_data['function'] = []

            if objects.memo:
                items_data['memo'] = objects.memo
            else:
                items_data['memo'] = '-'

            items_list.append(items_data)

        formatting_data = {
            'total': len(self.cmdb_data),
            'page': self.page,
            'limit': self.limit,
            'data': items_list,
            'msg': 'success',
            'status': 200,
        }

        return formatting_data

    def __parameter_check_handler(self, ):
        pass

    def __get_business_full_name(self, obj):
        return business_node_top(obj)

    def __get_business_admin_list(self, obj):
        return business_user_filter(obj, 'manager')

    def querybyip(self):
        if self.request_json_data.get('parameters').get('data'):
            search_list = self.request_json_data.get('parameters').get('data')
            self.cmdb_data = self.cmdb_data.filter(server__ipaddress__in=search_list)
            source_data = self.cmdb_data[self.start_tag: self.end_tag]
            response_data = self.__formatting_json(source_data)
        else:
            response_data = {'status': 502, 'msg': 'missing query data, please check.'}

        return response_data

    # def querybyhostip(self):
    #     if self.request_json_data.get('parameters').get('data'):
    #         search_list = self.request_json_data.get('parameters').get('data')
    #         self.cmdb_data = self.cmdb_data.filter(server__hosted_on__asset__nic__ipaddress__in=search_list)
    #         source_data = self.cmdb_data[self.start_tag: self.end_tag]
    #         response_data = self.__formatting_json(source_data)
    #     else:
    #         response_data = {'status': 502, 'msg': 'missing query data, please check.'}
    #
    #     return response_data

    def querybyidc(self):
        if self.request_json_data.get('parameters').get('data'):
            search_value = self.request_json_data.get('parameters').get('data')
            self.cmdb_data = self.cmdb_data.filter(idc__name__in=search_value)
            source_data = self.cmdb_data[self.start_tag: self.end_tag]
            response_data = self.__formatting_json(source_data)
        else:
            response_data = {'status': 502, 'msg': 'missing query data, please check.'}

        return response_data

    def querybyhostname(self):
        if self.request_json_data.get('parameters').get('data'):
            search_value = self.request_json_data.get('parameters').get('data')
            self.cmdb_data = self.cmdb_data.filter(server__hostname__in=search_value)
            source_data = self.cmdb_data[self.start_tag: self.end_tag]
            response_data = self.__formatting_json(source_data)
        else:
            response_data = {'status': 502, 'msg': 'missing query data, please check.'}

        return response_data

    def querybytype(self):
        if self.request_json_data.get('parameters').get('data'):
            search_value = self.request_json_data.get('parameters').get('data')
            asset_type_list = []
            asset_type_tuple = cmdb_models.Asset.device_type_choices
            for type_obj in asset_type_tuple:
                if type_obj[1] in search_value:
                    asset_type_list.append(type_obj[0])
            self.cmdb_data = self.cmdb_data.filter(device_type_id__in=asset_type_list)
            source_data = self.cmdb_data[self.start_tag: self.end_tag]
            response_data = self.__formatting_json(source_data)
        else:
            response_data = {'status': 502, 'msg': 'missing query data, please check.'}

        return response_data

    def querybybusiness(self):
        if self.request_json_data.get('parameters').get('data'):
            search_value = self.request_json_data.get('parameters').get('data')
            self.cmdb_data = self.cmdb_data.filter(business_unit__name__in=search_value)
            source_data = self.cmdb_data[self.start_tag: self.end_tag]
            response_data = self.__formatting_json(source_data)
        else:
            response_data = {'status': 502, 'msg': 'missing query data, please check.'}

        return response_data

    def querybydomain(self):
        if self.request_json_data.get('parameters').get('data'):
            search_value = self.request_json_data.get('parameters').get('data')
            source_data = {}
            if search_value == 'all':
                domain_data = OMTOOLS_MODELS.ProductDomains.objects.values('project_id__name', 'domain', 'productdomainsipaddr__ip_addr').all()
                for obj in domain_data:
                    if not source_data.get(obj['project_id__name']):
                        source_data[obj['project_id__name']] = {'ip_list': [], 'domain_list': []}
                    source_data[obj['project_id__name']]['domain_list'].append(obj['domain'])
                    source_data[obj['project_id__name']]['ip_list'].append(obj['productdomainsipaddr__ip_addr'])

            response_data = source_data
        else:
            response_data = {'status': 502, 'msg': 'missing query data, please check.'}

        return response_data
