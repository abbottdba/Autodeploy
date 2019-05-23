# -*- coding: utf-8 -*-

import json
from django.views import View
from django.shortcuts import render
from django.shortcuts import HttpResponse, HttpResponseRedirect
from utils.mixin_utils import LoginRequiredMixin, PermissionRequiredMixin, WriteAccessLogsMixin
from django.http import JsonResponse

from omtools.service import logs
from repository import models as REPOSITORY_MODELS
from omtools.models import LogsControl


class LogsIndexView(WriteAccessLogsMixin, View):
    def get(self, request):
        project_filter=request.GET.get('project', '')
        if project_filter == 'all':
            response = REPOSITORY_MODELS.ProjectInfo.objects.all()
        else:
            response = REPOSITORY_MODELS.ProjectInfo.objects.filter(name__in=project_filter.split(','))
        return render(request, 'omtools/logs_index.html', {'response': response})

    def post(self, request):
        response = mongodb.MongodbConfig.do_approval_by_id(request)
        return HttpResponseRedirect('/omtools/mongodb-approval.html?id=%s' % response.data.approval_md5)


class LogsDetailView(WriteAccessLogsMixin, View):
    def get(self, request, project_id):
        response = LogsControl.objects.filter(project_id__id=project_id).values('id', 'project_id__name', 'server_node',
                                                                                'server_type', 'logs_type', 'url',
                                                                                'logs_status', 'memo').order_by(
            'order_value')
        # return render(request, 'omtools/logs_detail.html', {'response': response})
        return HttpResponse(json.dumps(list(response)))
