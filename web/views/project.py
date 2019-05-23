#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
from django.views import View
from django.shortcuts import render
from django.shortcuts import HttpResponse, HttpResponseRedirect
from utils.mixin_utils import LoginRequiredMixin, PermissionRequiredMixin, WriteAccessLogsMixin
from django.http import JsonResponse
from web.service import project


class ProjectListView(WriteAccessLogsMixin, LoginRequiredMixin, PermissionRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'project_list.html')


class ProjectJsonView(WriteAccessLogsMixin, LoginRequiredMixin, PermissionRequiredMixin, View):
    def post(self, request):
        response = project.Project.add_data(request)
        return HttpResponseRedirect('/project.html')

    def get(self, request):
        obj = project.Project()
        response = obj.fetch_project(request)
        return JsonResponse(response.__dict__)

    def delete(self, request):
        response = project.Project.delete_data(request)
        return JsonResponse(response.__dict__)

    def put(self, request):
        response = project.Project.put_assets(request)
        return JsonResponse(response.__dict__)


class AddProjectView(WriteAccessLogsMixin, LoginRequiredMixin, PermissionRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # response = server_project.ServerProject.get_project_info(request)
        return render(request, 'add_project.html')


class UpdateProjectView(WriteAccessLogsMixin, LoginRequiredMixin, PermissionRequiredMixin, View):
    def get(self, request, project_nid):
        # project_info = server_project.ServerProject.get_project_info(request)
        response = project.Project.project_config(project_nid)
        return render(request, 'edit_project.html', {'response': response})


class ProjectAppViewsView(WriteAccessLogsMixin, LoginRequiredMixin, PermissionRequiredMixin, View):
    def get(self, request, project_nid):
        response = project.Project.project_config(project_nid)
        return render(request, 'project_appviews.html', {'response': response})


class ProjectProjectViewsView(WriteAccessLogsMixin, LoginRequiredMixin, PermissionRequiredMixin, View):
    def get(self, request, project_nid):
        response = project.Project.project_config(project_nid)
        return render(request, 'project_projectviews.html', {'response': response})

