# -*- coding: utf-8 -*-

import json, datetime
from django.views import View
from django.shortcuts import render
from django.shortcuts import HttpResponse, HttpResponseRedirect
from utils.mixin_utils import LoginRequiredMixin, PermissionRequiredMixin, WriteAccessLogsMixin
from django.http import JsonResponse

from omtools.service import logs
from repository import models as REPOSITORY_MODELS
from omtools.models import DnsMonitorControl
from omtools.models import ProductDomains
from django.http.request import QueryDict
from django.db.models import Count


class DnsMonitorIndexView(WriteAccessLogsMixin, View):
    def get(self, request):
        response = ProductDomains.objects.filter(status=False).order_by('project_id__name')
        domain_count = DnsMonitorControl.objects.values('project_id__name', 'project_id__cn_name').annotate(Count('domain'))
        current_date = datetime.datetime.now()
        return render(request, 'omtools/dnsmonitor_index.html', {'response': response, 'domain_count': domain_count, 'current_date': current_date})

    def post(self, request):
        request_data = request.body.decode('utf-8')
        request_json = json.loads(request_data)
        domain = request_json.get('domain')
        obj_from_db = ProductDomains.objects.filter(domain=domain)
        if obj_from_db:
            obj_from_db[0].status = False
            obj_from_db[0].update_date = datetime.datetime.now()
            obj_from_db[0].save()
        else:
            print('---domain not found--- %s' % domain)

        return HttpResponse(1)
