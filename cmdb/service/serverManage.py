#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json

from django.db.models import Q
from django.http.request import QueryDict

from cmdb import models
from utils.base import BaseServiceList
from utils.pager import PageInfo
from utils.response import BaseResponse

from cmdb.service import asset_num


class ServerManage(BaseServiceList):
    def __init__(self):
        # 查询条件的配置
        condition_config = [
            {'name': 'server__ipaddress', 'text': 'IP Address', 'condition_type': 'input'},
            {'name': 'device_type_id', 'text': 'Asset Type', 'condition_type': 'select', 'global_name': 'device_type_list'},
            {'name': 'device_status_id', 'text': 'Asset Status', 'condition_type': 'select','global_name': 'device_status_list'},
            {'name': 'idc', 'text': 'IDC', 'condition_type': 'select','global_name': 'idc_list'},
            {'name': 'sn', 'text': 'SN', 'condition_type': 'input'},
            {'name': 'rack', 'text': 'RACK', 'condition_type': 'input'},
        ]
        # 表格的配置
        table_config = [
            {
                'q': 'id',  # 用于数据库查询的字段，即Model.Tb.objects.filter(*[])
                'title': "ID",  # 前段表格中显示的标题
                'display': 0,  # 是否在前段显示，0表示在前端不显示, 1表示在前端隐藏, 2表示在前段显示
                'text': {'content': "{id}", 'kwargs': {'id': '@id'}},
                'attr': {'k1':'v1'}  # 自定义属性
            },
            {
                'q': 'server__ipaddress',
                'title': "IP Addr",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@server__ipaddress'}},
                'attr': {}
            },
            {
                'q': 'manage_ip',
                'title': "IDRAC IP",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@manage_ip'}},
                'attr': {'name': 'manage_ip', 'id': '@id', 'edit-enable': 'true', 'edit-type': 'input'}
            },
            {
                'q': 'sn',
                'title': "SN",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@sn'}},
                'attr': {}
            },
            {
                'q': 'idc_id',
                'title': "IDC",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@@idc_list'}},
                'attr': {'name': 'idc_id', 'id': '@idc_id', 'origin': '@idc_list', 'edit-enable': 'true',
                         'edit-type': 'select',
                         'global-name': 'idc_list'}
            },
            {
                'q': 'server__cpu_core_count',
                'title': "CPU",
                'display': 1,
                'text': {'content': "{n}C", 'kwargs': {'n': '@server__cpu_core_count'}},
                'attr': {}
            },
            {
                'q': 'server__Memory',
                'title': "RAM",
                'display': 1,
                'text': {'content': "{n}GB", 'kwargs': {'n': '@server__Memory'}},
                'attr': {}
            },
            {
                'q': 'server__DeviceSize',
                'title': "DISK",
                'display': 1,
                'text': {'content': "{n}GB", 'kwargs': {'n': '@server__DeviceSize'}},
                'attr': {}
            },
            {
                'q': 'raid_type',
                'title': "Raid",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@@raid_type_list'}},
                'attr': {'name': 'raid_type', 'id': '@raid_type', 'origin': '@raid_type_list', 'edit-enable': 'true',
                         'edit-type': 'select',
                         'global-name': 'raid_type_list'}
            },
            {
                'q': 'power_cable',
                'title': "Power",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@power_cable'}},
                'attr': {'name': 'power_cable', 'id': '@power_cable', 'edit-enable': 'true', 'edit-type': 'input'}
            },
            {
                'q': 'rack',
                'title': "RACK",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@rack'}},
                'attr': {'name': 'rack', 'id': '@rack', 'edit-enable': 'true', 'edit-type': 'input'}
            },
            {
                'q': 'device_type_id',
                'title': "Asset Type",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@@device_type_list'}},
                'attr': {'name': 'device_type_id', 'id': '@device_type_id', 'origin': '@device_type_list',
                         'edit-enable': 'true',
                         'edit-type': 'select',
                         'global-name': 'device_type_list'}
            },
            {
                'q': 'memo',
                'title': "Notes",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@memo'}},
                'attr': {'name': 'memo', 'id': '@id', 'edit-enable': 'true', 'edit-type': 'input'}
            },
            {
                'q': 'purchasing',
                'title': "Purchase Date",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@purchasing'}},
                'attr': {'name': 'purchasing', 'id': '@id', 'edit-enable': 'true', 'edit-type': 'input_date'}
            },
            {
                'q': None,
                'title': "Options",
                'display': 1,
                'text': {
                    'content': '<div class="btn-group"><a type="button" href="/cmdb/asset-detail-{nid}.html" class="btn btn-default btn-xs"><span class="glyphicon glyphicon-book" aria-hidden="true"></span> Detail</a></div>',
                    #'content': "<a href='/cmdb/asset-detail-{nid}.html'>查看详细</a> | <a href='/edit-asset-{device_type_id}-{nid}.html'>编辑</a>",
                    'kwargs': {'device_type_id': '@device_type_id', 'nid': '@id'}},
                'attr': {}
            },
        ]
        # 额外搜索条件
        extra_select = {
            # 'server_title': 'select hostname from cmdb_asset where device_type_id in [1];',
            # 'network_title': 'select management_ip from repository_networkdevice where repository_networkdevice.asset_id=repository_asset.id and repository_asset.device_type_id=2',
        }
        super(ServerManage, self).__init__(condition_config, table_config, extra_select)


    @property
    def device_status_list(self):
        result = map(lambda x: {'id': x[0], 'name': x[1]}, models.Asset.device_status_choices)
        return list(result)

    @property
    def device_type_list(self):
        result = map(lambda x: {'id': x[0], 'name': x[1]}, models.Asset.device_type_choices)
        return list(result)

    @property
    def idc_list(self):
        values = models.IDC.objects.only('id', 'name', 'floor')
        result = map(lambda x: {'id': x.id, 'name': x.name}, values)
        return list(result)

    @property
    def raid_type_list(self):
        result = map(lambda x: {'id': x[0], 'name': x[1]}, models.Asset.raid_type_choices)
        return list(result)

    @property
    def status_map(self):
        result = [
            {'id': 1, 'name': 'success'},
            {'id': 2, 'name': 'warning'},
            {'id': 3, 'name': 'danger'}
        ]
        return result

    @property
    def business_unit_list(self):
        values = models.BusinessUnit.objects.only('id', 'name')
        result = map(lambda x: {'id': x.id, 'name': x.name}, values)
        return list(result)

    @staticmethod
    def assets_condition(request):
        con_str = request.GET.get('condition', None)
        if not con_str:
            con_dict = {}
        else:
            con_dict = json.loads(con_str)

        con_q = Q()
        for k, v in con_dict.items():
            temp = Q()
            temp.connector = 'OR'
            for item in v:
                temp.children.append((k, item))
            con_q.add(temp, 'AND')

        return con_q

    def fetch_assets(self, request):
        response = BaseResponse()
        try:
            ret = {}
            conditions = self.assets_condition(request)
            asset_count = models.Asset.objects.filter(conditions, device_type_id__in=[1, 2, 4, 5]).count()
            page_info = PageInfo(request.GET.get('pager', None), asset_count)
            asset_list = models.Asset.objects.filter(conditions, device_type_id__in=[1, 2, 4, 5]).extra(select=self.extra_select).values(
                *self.values_list)[page_info.start:page_info.end]

            ret['table_config'] = self.table_config
            ret['condition_config'] = self.condition_config
            ret['data_list'] = list(asset_list)
            ret['page_info'] = {
                "page_str": page_info.pager(),
                "page_start": page_info.start,
            }
            ret['global_dict'] = {
                'device_status_list': self.device_status_list,
                'device_type_list': self.device_type_list,
                'idc_list': self.idc_list,
                'business_unit_list': self.business_unit_list,
                'status_map': self.status_map,
                'raid_type_list': self.raid_type_list
            }
            response.data = ret
            response.message = '获取成功'
        except Exception as e:
            response.status = False
            response.message = str(e)

        return response

    def asset_create(self):
        response = BaseResponse()
        try:
            ret = {}

            ret['asset_type'] = self.device_type_list
            ret['idc'] = self.idc_list

            response.data = ret
            response.message = '获取成功'
        except Exception as e:
            response.status = False
            response.message = str(e)

        return response

    def asset_data_create(request):
        response = BaseResponse()
        try:
            asset_data = QueryDict(request.body, encoding='utf-8')
            new_asset_num = asset_num.asset_num_builder()
            asset_sn = asset_data.get('sn')

            try:
                Memory = int(asset_data.get('Memory'))
            except:
                Memory = None
            try:
                DeviceSize = int(asset_data.get('DeviceSize'))
            except:
                DeviceSize = None
            try:
                cpu_count = int(asset_data.get('cpu_count'))
            except:
                cpu_count = None

            if not asset_sn:
                asset_sn = new_asset_num

            # 创建asset obj
            asset_obj = models.Asset(
                device_type_id = asset_data.get('device_type_id'),
                asset_num = new_asset_num,
                sn = asset_sn,
                idc_id = asset_data.get('idc_id'),
                business_unit_id = asset_data.get('business_unit_id'),
            )
            asset_obj.save()

            # 创建server obj
            server_obj = models.Server(
                asset_id = asset_obj.id,
                hostname = asset_data.get('hostname'),
                ipaddress = asset_data.get('ipaddress'),
                manage_ip = asset_data.get('manage_ip'),
                Memory = Memory,
                DeviceSize = DeviceSize,
                cpu_count = cpu_count,
            )
            server_obj.save()

            response.message = '获取成功'
        except Exception as e:
            print(Exception, e)
            response.status = False
            response.message = str(e)

        return response

    @staticmethod
    def delete_assets(request):
        response = BaseResponse()
        try:
            delete_dict = QueryDict(request.body, encoding='utf-8')
            id_list = delete_dict.getlist('id_list')
            models.Asset.objects.filter(id__in=id_list).delete()
            response.message = '删除成功'
        except Exception as e:
            response.status = False
            response.message = str(e)
        return response

    @staticmethod
    def put_assets(request):
        response = BaseResponse()
        try:
            response.error = []
            put_dict = QueryDict(request.body, encoding='utf-8')
            update_list = json.loads(put_dict.get('update_list'))
            error_count = 0
            for row_dict in update_list:
                nid = row_dict.pop('nid')
                num = row_dict.pop('num')
                try:
                    models.Asset.objects.filter(id=nid).update(**row_dict)
                except Exception as e:
                    response.error.append({'num': num, 'message': str(e)})
                    response.status = False
                    error_count += 1
            if error_count:
                response.message = '共%s条,失败%s条' % (len(update_list), error_count,)
            else:
                response.message = '更新成功'
        except Exception as e:
            response.status = False
            response.message = str(e)
        return response

    @staticmethod
    def assets_detail(asset_id):

        response = BaseResponse()
        try:
            print(asset_id)
            response.data = models.Asset.objects.filter(id=asset_id).first()

        except Exception as e:
            response.status = False
            response.message = str(e)
        return response