# -*- coding: utf-8 -*-

import json
from django.views import View
from django.shortcuts import render
from django.shortcuts import HttpResponse, HttpResponseRedirect
from utils.mixin_utils import LoginRequiredMixin, PermissionRequiredMixin, WriteAccessLogsMixin
from django.http import JsonResponse

from omtools.service import logs
from repository import models as REPOSITORY_MODELS
from omtools.models import UrlMapsControl


class UrlmapsIndexView(WriteAccessLogsMixin, LoginRequiredMixin, PermissionRequiredMixin, View):
    def get(self, request):
        response = REPOSITORY_MODELS.ProjectInfo.objects.all()
        return render(request, 'omtools/urlmaps_index.html', {'response': response})


class UrlmapsJsonView(WriteAccessLogsMixin, LoginRequiredMixin, PermissionRequiredMixin, View):
    def get(self, request, project_id):
        response = UrlMapsControl.objects.filter(project_id__id=project_id).values('id', 'project_id__name', 'url',
                                                                                'forward', 'nginx', 'ha',
                                                                                'backend', 'memo').order_by(
            'order_value')
        # return render(request, 'omtools/logs_detail.html', {'response': response})
        return HttpResponse(json.dumps(list(response)))
