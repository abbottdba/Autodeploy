#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
from django.views import View
from django.shortcuts import render
from django.shortcuts import HttpResponse, HttpResponseRedirect
from utils.mixin_utils import LoginRequiredMixin, PermissionRequiredMixin, WriteAccessLogsMixin
from django.http import JsonResponse

from cmdb.service import serverManage
from cmdb import models as CMDB_MODELS


class ServerManageListView(WriteAccessLogsMixin, LoginRequiredMixin, PermissionRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'cmdb_server_manage_list.html')


class ServerManageJsonView(WriteAccessLogsMixin, LoginRequiredMixin, PermissionRequiredMixin, View):
    def post(self, request):
        response = serverManage.ServerManage.asset_data_create(request)
        return JsonResponse(response.__dict__)

    def get(self, request):
        # obj = server.Server()
        response = serverManage.ServerManage().fetch_assets(request)
        return JsonResponse(response.__dict__)

    def delete(self, request):
        response = serverManage.ServerManage.delete_data(request)
        return JsonResponse(response.__dict__)

    def put(self, request):
        response = serverManage.ServerManage.put_assets(request)
        return JsonResponse(response.__dict__)