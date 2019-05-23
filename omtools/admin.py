from django.contrib import admin

from omtools import models

from django.contrib.admin import SimpleListFilter

admin.site.site_header = 'OM CMDB Admin'
admin.site.site_title = 'OM CMDB Admin'



class AccessLogsControl(admin.ModelAdmin):
    list_display = (
        'project_id', 'server_ip', 'server_node', 'server_type', 'logs_type', 'url', 'logs_status', 'order_value',
        'memo')
    search_fields = ('server_node', 'server_ip', 'server_type', 'logs_type', 'url', 'memo')
    list_display_links = ('project_id', 'server_ip', 'server_node', 'server_type', 'logs_type', 'url', 'memo')
    list_editable = ['logs_status', 'order_value']
    list_filter = ('project_id', 'server_ip', 'server_node', 'server_type', 'logs_status')


class AccessUrlmapsControl(admin.ModelAdmin):
    list_display = ('project_id', 'url', 'order_value', 'memo')
    search_fields = ('url', 'forward', 'nginx', 'ha', 'backend', 'memo')
    list_display_links = ('project_id', 'url', 'memo')
    list_editable = ['order_value']
    list_filter = ('project_id', )


class AccessProductDomains(admin.ModelAdmin):
    search_fields = ('domain', )


admin.site.register(models.MongodbMission)
admin.site.register(models.MongodbMissionTemplate)
admin.site.register(models.LogsControl, AccessLogsControl)
admin.site.register(models.UrlMapsControl, AccessUrlmapsControl)
admin.site.register(models.DnsMonitorControl)
admin.site.register(models.ProductDomains, AccessProductDomains)
admin.site.register(models.ProductDomainsIPaddr)


