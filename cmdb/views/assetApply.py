#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
from django.views import View
from django.shortcuts import render
from django.shortcuts import HttpResponse, HttpResponseRedirect
from utils.mixin_utils import LoginRequiredMixin, PermissionRequiredMixin, WriteAccessLogsMixin
from django.http import JsonResponse

from cmdb.service import assetApply
from cmdb import models as CMDB_MODELS
from user_center import models as user_center_models


class AssetApplyView(WriteAccessLogsMixin, LoginRequiredMixin, PermissionRequiredMixin, View):
    def post(self, request):
        response = assetApply.AssetApply.asset_apply_create(request)
        return JsonResponse(response.__dict__)

    def get(self, request, *args, **kwargs):
        idc_list = map(lambda x: {'id': x.id, 'name': x.name}, CMDB_MODELS.IDC.objects.all())
        asset_creator = map(lambda x: {'id': x['user_roles__id'], 'name': x['user_roles__username']},
                            user_center_models.Roles.objects.filter(
                                name='云主机配置管理').values('user_roles__id', 'user_roles__username'))
        function_list = map(lambda x: {'id': x.id, 'name': x.name}, CMDB_MODELS.Tag.objects.order_by('order_id'))
        ret_data = {
            'idc_list' : idc_list,
            'asset_creator': asset_creator,
            'function_list': function_list,
        }
        return render(request, 'cmdb/cmdb_asset_apply.html', ret_data)


class AssetApplyListView(WriteAccessLogsMixin, LoginRequiredMixin, PermissionRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'cmdb/cmdb_asset_apply_list.html')


class AssetApplyListJsonView(WriteAccessLogsMixin, LoginRequiredMixin, PermissionRequiredMixin, View):
    def post(self, request):
        response = server.Server.asset_data_create(request)
        return JsonResponse(response.__dict__)

    def get(self, request):
        # obj = server.Server()
        response = assetApply.AssetApply().fetch_data(request)
        return JsonResponse(response.__dict__)

    def delete(self, request):
        response = server.Server.delete_data(request)
        return JsonResponse(response.__dict__)

    def put(self, request):
        response = server.Server.put_assets(request)
        return JsonResponse(response.__dict__)


class AssetApplyDetailView(WriteAccessLogsMixin, LoginRequiredMixin, PermissionRequiredMixin, View):
    def get(self, request, order_id):
        data = CMDB_MODELS.ServerApplyOrder.objects.get(id=order_id)
        return render(request, 'cmdb/cmdb_asset_apply_detail.html', {"order_id": order_id, 'data': data})

    def put(self, request, order_id):
        response = assetApply.AssetApply.update_apply_order(request, order_id)
        return JsonResponse(response.__dict__)


class AssetApplyDetailJsonView(WriteAccessLogsMixin, LoginRequiredMixin, PermissionRequiredMixin, View):
    def get(self, request, order_id):
        response = assetApply.AssetApply.get_apply_json(request, order_id)
        return JsonResponse(response.__dict__)

    def put(self, request, order_id):
        response = assetApply.AssetApply.update_apply_items(request, order_id)
        return JsonResponse(response.__dict__)
