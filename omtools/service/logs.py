import json, time
import subprocess
import hashlib

from django.db.models import Q
from django.http.request import QueryDict

from omtools import models as OMTOOLS_MODELS
from utils.base import BaseServiceList
from utils.pager import PageInfo
from utils.response import BaseResponse

from omtools.cores import redis_handler
from utils import smtp
from conf import settings
import datetime
from bson import ObjectId


class MongodbConfig(BaseServiceList):
    def __init__(self):
        # 查询条件的配置
        condition_config = [
            {'name': 'url_name', 'text': 'URL Name', 'condition_type': 'input'},
            {'name': 'url_method', 'text': 'URL Method', 'condition_type': 'select', 'global_name': 'url_method_list'},
        ]
        # 表格的配置
        table_config = [
            {
                'q': 'id',  # 用于数据库查询的字段，即Model.Tb.objects.filter(*[])
                'title': "ID",  # 前段表格中显示的标题
                'display': 0,  # 是否在前段显示，0表示在前端不显示, 1表示在前端隐藏, 2表示在前段显示
                'text': {'content': "{id}", 'kwargs': {'id': '@id'}},
                'attr': {'k1': 'v1'}  # 自定义属性
            },
            {
                'q': 'title',
                'title': "Mission Name",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@title'}},
                'attr': {}
            },
            {
                'q': 'database',
                'title': "Database",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@database'}},
                'attr': {}
            },
            {
                'q': 'document',
                'title': "Document",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@document'}},
                'attr': {}
            },
            {
                'q': 'op_type',
                'title': "Mission Type",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@@op_type_list'}},
                'attr': {}
            },
            {
                'q': 'req_user__username',
                'title': "Request User",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@req_user__username'}},
                'attr': {}
            },
            {
                'q': 'op_user__username',
                'title': "Option User",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@op_user__username'}},
                'attr': {}
            },
            {
                'q': 'status',
                'title': "Status",
                'display': 1,
                'text': {'content': '<a type="button" class="btn btn-{class} btn-xs">{n}</a>',
                         'kwargs': {'n': '@@option_status', 'class': '@@status_map'}
                         },
                'attr': {}
            },
            {
                'q': 'date',
                'title': "Date",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@date'}},
                'attr': {}
            },
            {
                'q': 'memo',
                'title': "Memo",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@memo'}},
                'attr': {}
            },
            {
                'q': None,
                'title': "Options",
                'display': 1,
                'text': {
                    'content': '<div class="btn-group">' +
                               '<a type="button" class="btn btn-default btn-xs" onclick="show_mission_detail_fn({nid})"><span class="glyphicon glyphicon-search" aria-hidden="true"></span> 命令查看</a>' +
                               '<a type="button" class="btn btn-default btn-xs" onclick="show_mission_opdetail_fn({nid})"><span class="glyphicon glyphicon-list-alt" aria-hidden="true"></span> 执行结果</a>' +
                               '</div>',
                    'kwargs': {'nid': '@id'}},
                'attr': {'style': 'text-align: left; width: 260px'}
            },
        ]
        # 额外搜索条件
        extra_select = {
            'server_title': '',
            # 'network_title': 'select management_ip from repository_networkdevice where repository_networkdevice.asset_id=repository_asset.id and repository_asset.device_type_id=2',
        }
        super(MongodbConfig, self).__init__(condition_config, table_config, extra_select)

    @property
    def op_type_list(self):
        result = map(lambda x: {'id': x[0], 'name': x[1]}, OMTOOLS_MODELS.MongodbMission.op_type_choices)
        return list(result)

    @property
    def option_status(self):
        result = map(lambda x: {'id': x[0], 'name': x[1]}, OMTOOLS_MODELS.MongodbMission.status_choices)
        return list(result)

    @property
    def status_map(self):
        result = [
            {'id': 1, 'name': 'success'},
            {'id': 2, 'name': 'danger'},
            {'id': 3, 'name': 'warning'},
        ]
        return result

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

    def fetch_data(self, request):
        response = BaseResponse()
        try:
            ret = {}
            conditions = self.assets_condition(request)
            asset_count = OMTOOLS_MODELS.MongodbMission.objects.filter(conditions).count()
            page_info = PageInfo(request.GET.get('pager', None), asset_count)
            asset_list = OMTOOLS_MODELS.MongodbMission.objects.filter(conditions).order_by('-id').extra(
                select=self.extra_select).values(
                *self.values_list)[page_info.start:page_info.end]

            ret['table_config'] = self.table_config
            ret['condition_config'] = self.condition_config
            ret['data_list'] = list(asset_list)
            ret['page_info'] = {
                "page_str": page_info.pager(),
                "page_start": page_info.start,
            }
            ret['global_dict'] = {
                'op_type_list': self.op_type_list,
                'option_status': self.option_status,
                'status_map': self.status_map,
            }
            response.data = ret
            response.message = '获取成功'
        except Exception as e:
            response.status = False
            response.message = str(e)

        return response

    @staticmethod
    def data_create(request):
        response = BaseResponse()
        try:
            post_data = QueryDict(request.body, encoding='utf-8')
            mongoMission_template_id = post_data.get('mongoMission_template_id')
            mongoMission_memo = post_data.get('mongoMission_memo')

            template_data = OMTOOLS_MODELS.MongodbMissionTemplate.objects.get(id=int(mongoMission_template_id))
            var_list = json.loads(template_data.var_dict)

            m_db = template_data.database
            m_document = template_data.document
            m_op_type = template_data.get_op_type_display()
            m_find = template_data.find
            m_update = template_data.update
            m_multi_tag = template_data.multi_tag

            def __json_val_check(json_val):
                for k, v in json_val.items():
                    if type(v) == dict:
                        __json_val_check(v)
                    else:
                        try:
                            if 'ISODate' in v:
                                json_val[k] = datetime.datetime.strptime(v.split('~')[1], '%Y-%m-%d %H:%M:%S')
                            if 'ObjectId' in v:
                                json_val[k] = ObjectId(v.split('~')[1])
                        except:
                            continue

            for k, v in post_data.items():
                if '$$' in k:
                    # 根据名称查找变量参数
                    for var_obj in var_list:
                        if k == var_obj['var_name']:
                            if var_obj['choice'] == 'LIST':
                                var = str(v.split('\r\n'))
                            else:
                                try:
                                    var = json.loads(v)
                                    __json_val_check(var)
                                except:
                                    var = v

                            m_find = m_find.replace(k, str(var))
                            # m_find = m_find.replace("'", '"')
                            if m_update:
                                m_update = m_update.replace(k, var)
                                # m_update = m_update.replace("'", '"')
                            else:
                                m_update = {}

            # 生成exec语句
            if m_op_type == 'update':
                option_exec = "%s.%s.update(%s, %s, {'multi':%s})" % (m_db, m_document, m_find, m_update, m_multi_tag)
            elif m_op_type == 'find':
                option_exec = "%s.%s.find(%s)" % (m_db, m_document, m_find)
            else:
                option_exec = None

            print(option_exec)

            # 生成任务md5值，用于邮件审批
            Token_STR = 'NEBB5oMQOPMpLTn6PneJKBDEMU0WeBxd'
            time_stamp = str(int(time.time()))
            md5_value = hashlib.md5(str(Token_STR + time_stamp).encode('utf-8'))

            # 创建Mission
            data_obj = OMTOOLS_MODELS.MongodbMission(
                title=template_data.title,
                op_type=template_data.op_type,
                op_exec=option_exec,
                database=m_db,
                document=m_document,
                find=m_find,
                update=m_update,
                multi_tag=m_multi_tag,
                req_user_id=request.user.id,
                approval_md5=md5_value.hexdigest(),
                memo=mongoMission_memo,
            )
            data_obj.save()

            # 调用邮件接口，发送审核邮件
            approval_email = template_data.approve_mail
            mail_title = 'MongoDB自助任务审核 - %s' % template_data.title
            approval_url = "http://cmdb_cloud.omtools.me:9991/omtools/mongodb-approval.html?id=%s" % md5_value.hexdigest()
            mail_content = "申请执行以下语句：<br><br>%s<br><br>审批地址：<a href='%s'>%s</a>" % (option_exec, approval_url, approval_url)
            # smtp.sendMail("noreply@m1om.me", "bananaballs123!", [approval_email], mail_title, mail_content)
            send_mail = subprocess.Popen([settings.pyenv, './utils/smtp.py', approval_email, mail_title, mail_content])

        except Exception as e:
            print(Exception, e)
            response.status = False
            response.message = str(e)

        return response

    @staticmethod
    def data_update(request):
        response = BaseResponse()
        try:
            put_data = QueryDict(request.body, encoding='utf-8')
            obj_id = put_data.get('id')

            update_data = OMTOOLS_MODELS.MongodbMission.objects.get(id=obj_id)
            update_data.op_user_id = request.user.id
            update_data.status = 1
            update_data.save()

        except Exception as e:
            print(Exception, e)
            response.status = False
            response.message = str(e)
        return response

    @staticmethod
    def get_permission_data():

        response = BaseResponse()
        try:
            response.data = USER_CENTER_MODELS.Permission.objects.all().order_by('-id')

        except Exception as e:
            response.status = False
            response.message = str(e)
        return response

    @staticmethod
    def get_detail_by_id(request):
        response = BaseResponse()
        try:
            obj_id = request.GET.get('id')
            response.data = OMTOOLS_MODELS.MongodbMission.objects.filter(id=obj_id).values().first()

        except Exception as e:
            response.status = False
            response.message = str(e)
        return response

    @staticmethod
    def get_template_by_id(request):
        response = BaseResponse()
        try:
            template_id = request.GET.get('template_id')
            response.data = OMTOOLS_MODELS.MongodbMissionTemplate.objects.filter(id=template_id).values().first()

        except Exception as e:
            response.status = False
            response.message = str(e)
        return response

    @staticmethod
    def get_template_data():
        response = BaseResponse()
        try:
            response.data = OMTOOLS_MODELS.MongodbMissionTemplate.objects.all()
        except Exception as e:
            response.status = False
            response.message = str(e)
        return response

    @staticmethod
    def get_approval_by_id(request):
        response = BaseResponse()
        try:
            md5_id = request.GET.get('id')
            response.data = OMTOOLS_MODELS.MongodbMission.objects.get(approval_md5=md5_id)
        except Exception as e:
            response.status = False
            response.message = str(e)
        return response

    @staticmethod
    def do_approval_by_id(request):
        response = BaseResponse()
        try:
            md5_id = request.POST.get('id')
            mission_obj = OMTOOLS_MODELS.MongodbMission.objects.get(approval_md5=md5_id)
            response.data = mission_obj

            # 更新任务状态
            mission_obj.approved = True
            mission_obj.save()

            # 向redis接口提交任务
            redis_queue = redis_handler.RedisQueue('mongodb')
            redis_queue.put(mission_obj.id)

        except Exception as e:
            response.status = False
            response.message = str(e)
        return response
