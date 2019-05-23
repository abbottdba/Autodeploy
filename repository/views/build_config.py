#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
from django.views import View
from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.http import JsonResponse
from utils.mixin_utils import LoginRequiredMixin, PermissionRequiredMixin, WriteAccessLogsMixin

from repository import models
from repository.service.deploy import main_handler

from repository.conf import settings


class BuildConfigView(WriteAccessLogsMixin, LoginRequiredMixin, PermissionRequiredMixin, View):
    def get(self, request, server_id):
        # response = domains_config.ServerDomains.get_server_domains(server_id)
        response = models.Applications.objects.get(id=server_id)
        return render(request, 'server_config_build.html', {'response': {'data': response}})

    def post(self, request, server_id):
        app_obj = models.Applications.objects.get(id=server_id)
        app_obj.build = True
        app_obj.save()
        docker_build = main_handler.FaucetControl(app_obj.name, app_obj.app_type, 'cstest', app_obj.cstest_port)
        docker_build.sync_cstest()
        return HttpResponse(1)


class GetBuildLogsView(WriteAccessLogsMixin, LoginRequiredMixin, PermissionRequiredMixin, View):
    def get(self, request, server_id):
        app_obj = models.Applications.objects.get(id=server_id)
        f = settings.docker_deploy_log.format(app_name=app_obj.name)
        f = open(f, 'rb')
        read_data = f.read()
        f.close()
        app_build_log = read_data.decode(encoding='utf-8')
        return HttpResponse(app_build_log)