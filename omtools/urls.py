from django.conf.urls import url
from omtools.views import mongodb
from omtools.views import logs
from omtools.views import urlmaps
from omtools.views import dnsmonitor

from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^mongodb.html$', mongodb.MongodbListView.as_view(), name='omtools-mongodb-list'),
    url(r'^mongodb-json.html$', mongodb.MongodbJsonView.as_view(), name='omtools-mongodb-json'),
    url(r'^mongodb-get-detail.html$', mongodb.MongodbDetailView.as_view(), name='omtools-mongodb-detail'),
    url(r'^mongodb-get-template.html$', mongodb.MongodbTemplateView.as_view(), name='omtools-mongodb-template'),
    url(r'^mongodb-approval.html$', mongodb.MongodbApprovalView.as_view(), name='omtools-mongodb-approval'),
    url(r'^logs.html$', logs.LogsIndexView.as_view(), name='omtools-logs-index'),
    url(r'^logs-(?P<project_id>\d+).html$', logs.LogsDetailView.as_view(), name='omtools-logs-detail'),
    url(r'^urlmaps.html$', urlmaps.UrlmapsIndexView.as_view(), name='omtools-urlmaps-index'),
    url(r'^urlmaps-(?P<project_id>\d+).html$', urlmaps.UrlmapsJsonView.as_view(), name='omtools-logs-detail'),
    url(r'^dnsmonitor.html$', dnsmonitor.DnsMonitorIndexView.as_view(), name='omtools-dnsmonitor-index'),
]
