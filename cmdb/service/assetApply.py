#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json

from django.db.models import Q
from django.http.request import QueryDict

from cmdb import models
from utils.base import BaseServiceList
from utils.pager import PageInfo
from utils.response import BaseResponse
from utils.public_utils import business_node_low
from utils import email_smtp

from cmdb.service import asset_num
from utils.public_utils import business_node_top
from utils.public_utils import log_handler

from user_center import models as user_center_models

class AssetApply(BaseServiceList):
    def __init__(self):
        # 查询条件的配置
        condition_config = [
            {'name': 'name', 'text': 'Order Name', 'condition_type': 'input'},
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
                'q': 'name',
                'title': "Order Name",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@name'}},
                'attr': {}
            },
            {
                'q': 'order_type',
                'title': "Order Type",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@@order_type_list'}},
                'attr': {}
            },
            {
                'q': 'business',
                'title': "Business Unit",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@@business_unit_list'}},
                'attr': {}
            },
            {
                'q': 'user_apply',
                'title': "Apply User",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@user_apply'}},
                'attr': {}
            },
            {
                'q': 'approved',
                'title': "Approved",
                'display': 1,
                'text': {'content': '<a type="button" class="btn btn-{n1} btn-xs">{n2}</a>', 'kwargs': {'n1': '@@status_class_map', 'n2': '@@status_name_map'}},
                'attr': {}
            },
            {
                'q': 'date_apply',
                'title': "Apply Date",
                'display': 0,
                'text': {'content': "{n}", 'kwargs': {'n': 1}},
                'attr': {}
            },
            {
                'q': 'id',
                'title': "Apply Date",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@@date_list'}},
                'attr': {}
            },
            {
                'q': None,
                'title': "Options",
                'display': 1,
                'text': {
                    'content': '<div class="btn-group"><a type="button" class="btn btn-default btn-xs" href="/cmdb/apply/list/{id}.html"><span class="glyphicon glyphicon-edit" aria-hidden="true"></span> Config</a>  </div>',
                    'kwargs': {'id': '@id'}},
                'attr': {}
            },
        ]
        # 额外搜索条件
        extra_select = {
            'server_title': 'select hostname from cmdb_server where cmdb_server.asset_id=cmdb_asset.id and cmdb_asset.device_type_id=1',
            # 'network_title': 'select management_ip from repository_networkdevice where repository_networkdevice.asset_id=repository_asset.id and repository_asset.device_type_id=2',
        }
        super(AssetApply, self).__init__(condition_config, table_config, extra_select)

    @property
    def order_type_list(self):
        result = map(lambda x: {'id': x[0], 'name': x[1]}, models.ServerApplyOrder.order_type_choices)
        return list(result)

    @property
    def status_class_map(self):
        result = [
            {'id': False, 'name': 'danger'},
            {'id': True, 'name': 'success'},
        ]
        return result

    @property
    def status_name_map(self):
        result = [
            {'id': False, 'name': 'Pending'},
            {'id': True, 'name': 'Approved'},
        ]
        return result

    @property
    def business_unit_list(self):
        def business_node_top(obj, node_name):
            if obj.parent_unit:
                parent_name = business_node_top(obj.parent_unit, node_name)
                node_name = '%s-%s' %(parent_name, obj.name)
                return node_name
            else:
                return obj.name

        get_data = models.BusinessUnit.objects.all()
        business_list = []
        for obj in get_data:
            node_name = business_node_top(obj, '')
            business_list.append({'id': obj.id, 'name': node_name})

        return business_list

    @property
    def tag_list(self):
        values = models.Tag.objects.only('id', 'name')
        result = map(lambda x: {'id': x.id, 'name': x.name}, values)
        return list(result)

    @property
    def date_list(self):
        result = map(lambda x: {'id': x.get('id'), 'name': x.get('date_apply').strftime('%Y-%m-%d %H:%M:%S')}, self.asset_list)
        return list(result)

    @staticmethod
    def assets_condition(request):
        con_str = request.GET.get('condition', None)
        if not con_str:
            con_dict = {}
        else:
            con_dict = json.loads(con_str)

        # 查询子类业务线
        if con_dict.get('business_unit'):
            b_id = con_dict['business_unit']
            business_obj = models.BusinessUnit.objects.get(id__in=b_id)
            business_node_with_child = business_node_low(business_obj)
            if '-' in business_node_with_child:
                con_dict['business_unit'] = business_node_with_child.split('-')

        con_q = Q()
        for k, v in con_dict.items():
            temp = Q()
            temp.connector = 'OR'
            for item in v:
                temp.children.append((k, item))
            con_q.add(temp, 'AND')

        return con_q

    def fetch_data(self, request):
        response = BaseResponse()
        try:
            ret = {}
            conditions = self.assets_condition(request)
            asset_count = models.ServerApplyOrder.objects.filter(conditions).count()
            page_info = PageInfo(request.GET.get('pager', None), asset_count)
            asset_list = models.ServerApplyOrder.objects.filter(conditions).extra(select=self.extra_select).values(
                *self.values_list).order_by('-id')[page_info.start:page_info.end]
            self.asset_list = asset_list
            ret['table_config'] = self.table_config
            ret['condition_config'] = self.condition_config
            ret['data_list'] = list(asset_list)
            ret['page_info'] = {
                "page_str": page_info.pager(),
                "page_start": page_info.start,
            }
            ret['global_dict'] = {
                'business_unit_list': self.business_unit_list,
                'status_class_map': self.status_class_map,
                'status_name_map': self.status_name_map,
                'order_type_list': self.order_type_list,
                'date_list': self.date_list,
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
            ret['tag'] = self.tag_list

            response.data = ret
            response.message = '获取成功'
        except Exception as e:
            response.status = False
            response.message = str(e)

        return response

    def asset_apply_create(request):
        response = BaseResponse()
        try:
            apply_data = dict(QueryDict(request.body, encoding='utf-8'))
            title = apply_data.get('title')
            os_type = apply_data.get('os_type')
            idc = apply_data.get('idc')
            business_unit_id = apply_data.get('business_unit_id')
            creator = apply_data.get('creator')
            apply_list = apply_data.get('apply_list')

            # 创建任务申请
            add_order = models.ServerApplyOrder(
                name = title[0],
                order_type = 1,
                business=business_unit_id[0],
                user_apply = request.user.username,
            )

            add_order.save()

            if apply_list:
                config_json_data = json.loads(apply_list[0])
                for asset_obj in config_json_data:
                    # 创建asset申请详情
                    add_asset = models.ServerApplyDetail.objects.create(
                        idc = idc[0],
                        sys_type = os_type[0],
                        user_apply = request.user.username,
                        **asset_obj,
                    )
                    add_asset.save()
                    add_order.project.add(add_asset)

            # 任务创建成功，调用邮件接口 - 发送至任务接收人
            send_to = creator[0] + '@m1om.me,'
            email_smtp.mail_send(send_to, 'asset_apply_create', {'title': title[0], 'creator': creator[0], 'id': add_order.id})

            # 创建日志
            log_handler(
                asset_id=None,
                event_type=4,
                detail='%s apply %s hosts from cloud server' %(request.user.username, len(apply_list) ),
                user=request.user,
            )

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
        def __update_asset_tag(nid, tag_obj):
            asset_obj = models.Asset.objects.get(id=nid)
            if int(tag_obj['tag__id']) not in [i.id for i in asset_obj.tag.all()]:
                asset_obj.tag.clear()
                asset_obj.tag.add(tag_obj['tag__id'])
        def __update_asset_configuration(nid, config_obj):
            asset_obj = models.Asset.objects.get(id=nid)
            print(config_obj)
        try:
            response.error = []
            put_dict = QueryDict(request.body, encoding='utf-8')
            update_list = json.loads(put_dict.get('update_list'))
            error_count = 0
            for row_dict in update_list:
                nid = row_dict.pop('nid')
                num = row_dict.pop('num')
                try:
                    if row_dict.get('tag__id'):
                        __update_asset_tag(nid, {'tag__id': row_dict.pop('tag__id')})
                    if row_dict.get('server__configuration'):
                        __update_asset_configuration(nid, {'server__configuration': row_dict.pop('server__configuration')})
                    models.Asset.objects.filter(id=nid).update(**row_dict)
                except Exception as e:
                    print(Exception, e)
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

    def get_apply_json(request, order_id):
        response = BaseResponse()

        try:
            order_obj = models.ServerApplyOrder.objects.get(id=order_id)
            get_order_detail_from_db = models.ServerApplyDetail.objects.filter(server_apply_order__id=order_id).values()
            for asset_obj in get_order_detail_from_db:
                business_obj = models.BusinessUnit.objects.filter(id=order_obj.business)
                if business_obj:
                    asset_obj['business'] = business_node_top(business_obj[0])
                else:
                    asset_obj['business'] = '-'
            response.data = list(get_order_detail_from_db)

        except Exception as e:
            print(Exception, e)
            response.status = False
            response.message = str(e)

        return response

    def update_apply_items(request, order_id):
        response = BaseResponse()
        update_data = QueryDict(request.body, encoding='utf-8')
        obj_id = update_data.get('obj_id')
        ipaddress = update_data.get('ipaddress')

        try:
            # 检查更新ip地址是否存在
            check_exist_server = models.Server.objects.filter(ipaddress=ipaddress)
            if not check_exist_server:
                get_item_from_db = models.ServerApplyDetail.objects.get(id=obj_id)
                get_item_from_db.ipaddress = ipaddress
                get_item_from_db.approved = 2
                get_item_from_db.save()
            else:
                response.status = False
                response.message = 'This IP has already exist in CMDB, Please check again.'

        except Exception as e:
            print(Exception, e)
            response.status = False
            response.message = str(e)

        return response

    def update_apply_order(request, order_id):
        response = BaseResponse()
        update_data = QueryDict(request.body, encoding='utf-8')
        order_id = update_data.get('order_id')

        try:

            apply_order_data = models.ServerApplyOrder.objects.filter(id=order_id)

            if apply_order_data:
                apply_order_obj = apply_order_data[0]
                for asset_obj in apply_order_obj.project.all():
                    try:
                        cmdb_asset_obj = models.Asset(
                            device_type_id = 3,
                            asset_num = asset_num.asset_num_builder(),
                            sn = asset_num.asset_num_builder(),
                            idc = models.IDC.objects.get(name=asset_obj.idc),
                            business_unit = models.BusinessUnit.objects.get(id=apply_order_obj.business),
                            memo = asset_obj.memo,
                            creator = user_center_models.UserProfile.objects.get(username=request.user.username)
                        )
                        cmdb_asset_obj.save()
                        cmdb_asset_obj.tag.add(models.Tag.objects.get(name=asset_obj.function))

                        # 创建资产日志
                        log_handler(
                            asset_id = cmdb_asset_obj.id,
                            event_type=1,
                            detail = 'Server Created, apply user is %s' % apply_order_obj.user_apply,
                            user = request.user
                        )
                    except Exception as e:
                        print(e)
                        cmdb_asset_obj.delete()
                        asset_obj.approved = 4
                        asset_obj.save()
                        continue

                    try:
                        cmdb_server_obj = models.Server(
                            asset = cmdb_asset_obj,
                            ipaddress = asset_obj.ipaddress,
                            configuration = '( %sC /%sG /%sG )' % (asset_obj.cpu, asset_obj.mem, asset_obj.disk),
                            cpu_count = asset_obj.cpu,
                            Memory = asset_obj.mem,
                            DeviceSize = asset_obj.disk,
                            os_type = asset_obj.sys_type,
                        )
                        cmdb_server_obj.save()
                    except Exception as e:
                        print(e)
                        cmdb_asset_obj.delete()
                        asset_obj.approved = 4
                        asset_obj.save()
                        continue

                    asset_obj.approved = 3
                    asset_obj.save()

                # 更新任务单状态 这个地方注意一下更新的顺序，放在这里有点问题，上面失败，下面也会被更新
                apply_order_obj.approved = True
                apply_order_obj.user_approve = request.user.username
                apply_order_obj.save()

                asset_detail_json = list(apply_order_obj.project.values())

                # 任务创建完成，通知组内成员
                send_to = ''
                business_obj = models.BusinessUnit.objects.filter(id=apply_order_obj.business)
                for user_groups in business_obj[0].manager.all():
                    for user in user_groups.users.all():
                        send_to += user.username + '@m1om.me,'

                template_var = {
                    'title': apply_order_obj.name,
                    'json_data': asset_detail_json,
                    'business_unit': business_node_top(business_obj[0]),
                    'user_apply': apply_order_obj.user_apply,
                    'user_approve': apply_order_obj.user_approve,
                    'server_count': len(asset_detail_json)
                }
                email_smtp.mail_send(send_to, 'asset_apply_create_inform_group', template_var)

        except Exception as e:
            print(Exception, e)
            response.status = False
            response.message = str(e)

        return response

