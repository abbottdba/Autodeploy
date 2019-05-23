#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
from django.views import View
from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.http import JsonResponse
from utils.mixin_utils import LoginRequiredMixin, PermissionRequiredMixin, WriteAccessLogsMixin

from repository.service import domains_config


class DomainsConfigView(WriteAccessLogsMixin, LoginRequiredMixin, PermissionRequiredMixin, View):
    def get(self, request, server_id):
        response = domains_config.ServerDomains.get_server_domains(server_id)
        return render(request, 'server_config_domains.html', {'response': response})


class DomainsConfigJsonView(WriteAccessLogsMixin, LoginRequiredMixin, PermissionRequiredMixin, View):
    def get(self, request, server_id):
        response = domains_config.ServerDomains.get_server_domains_json(server_id)
        return HttpResponse(json.dumps(response.data))


class UpdateDomainView(WriteAccessLogsMixin, LoginRequiredMixin, PermissionRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        response = domains_config.ServerDomains.get_domain_by_id(request)
        return HttpResponse(json.dumps(response))

    def post(self, request):
        response = domains_config.ServerDomains.add_domain(request)
        return JsonResponse(response.__dict__)

    def put(self, request):
        response = domains_config.ServerDomains.update_domain(request)
        return JsonResponse(response.__dict__)

    def delete(self, request):
        response = domains_config.ServerDomains.delete_domain(request)
        return JsonResponse(response.__dict__)